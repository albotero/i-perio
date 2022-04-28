#!/usr/bin/python3

from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit

from scripts.diente import Diente, get_titulos
from scripts.grafico import nuevo_canvas
from scripts.guardar_perio import Guardar
from scripts.log import Log
from scripts.main import nuevo_perio
from scripts.process_images import actualizar_imagenes
from scripts.usuarios import valor_credito, Usuario

from datetime import datetime
from babel.dates import format_datetime
import pytz

import os
import uuid

import mercadopago as mp
import requests
import json # prueba solo para print

app = Flask(__name__, instance_relative_config = True)
app.secret_key = 'perio'
app.debug = True

socketio = SocketIO(app, cors_allowed_origins = '*', async_mode='gevent') #, logger=True, engineio_logger=True)

os.chdir(os.path.dirname(__file__))

if app.debug:
    # Pruebas
    mp_access_token = 'TEST-5314041922096496-083002-55909990b064c9ba4c1bfad56a2b6a51-61341214'
    mp_public_key = 'TEST-b02a8226-f0de-404f-ad06-ef30edb58dec'
else:
    # Producción
    mp_access_token = 'APP_USR-5314041922096496-083002-a9b9979144558e5fae30d3e2d10097a5-61341214'
    mp_public_key = 'APP_USR-892809af-d19e-4f7b-bc7e-a101e7566d33'
mp_sdk = mp.SDK(mp_access_token)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Verifica que esté loggeado
    if 'usuario' not in session:
        return redirect(url_for('login'))

    orden = request.values.get('orden', 'modificacion')
    desc = request.values.get('desc', 'true').lower() == 'true'
    tipos_orden = {
        'creacion': 'Fecha de Creaci&oacute;n',
        'modificacion': '&Uacute;ltima Modificaci&oacute;n'
    }

    perios = Guardar.list_perios(session['usuario'], orden, desc)

    return render_template('index.html',
                            usuario = session['usuario'],
                            perios_guardados = perios,
                            orden = orden,
                            desc = desc,
                            tipos_orden = tipos_orden)

@app.route('/perio/')
def perio():
    # Verifica que tenga créditos suficientes
    creditos, _ = consultar_creditos()
    if creditos == 0:
        return redirect(url_for('creditos'))

    # Genera un archivo temporal para guardar el perio
    filename = uuid.uuid4().hex
    perio = nuevo_perio()

    Guardar.perio_to_file(
                perio,
                archivo = filename,
                id_usuario = session['usuario'],
                silent = True)

    return redirect(url_for('.cargar_perio', usuario=session['usuario'], id_perio=filename))

@app.route('/perio/<int:usuario>/<id_perio>')
def cargar_perio(usuario, id_perio):
    # Verifica que tenga créditos suficientes
    creditos, _ = consultar_creditos()
    if creditos == 0:
        return redirect(url_for('creditos'))

    # Verifica si tiene acceso al archivo
    # Por ahora solo verifica si es el propietario
    if session['usuario'] != usuario:
        return 'No tiene acceso a este perio'

    # Carga un perio existente
    try:
        perio = Guardar.file_to_perio(
                            archivo=id_perio,
                            id_usuario=usuario,
                            silent = True,
                            throwerror = True)
    except Exception as ex:
        return f'ID inv&aacute;lido<br/>{ex}'

    # Declaración de variables
    dict_perio = { 'sup': {}, 'inf': {} }
    primer_diente = [18, 48]

    # Obtiene los encabezados de las filas
    for d in primer_diente:
        diente = Diente(d)
        grupo = 'sup' if diente['superior'] else 'inf'
        dict_perio[grupo]['titulos'] = get_titulos(diente)

    # Agrega el diente al grupo correspondiente
    for num, diente in perio.items():
        if not num.isnumeric():
            continue

        # Si hace parte del perio superior o del inferior
        grupo = 'sup' if diente['superior'] else 'inf'
        dict_perio[grupo][int(num)] = diente

    # Obtiene los str de las imágenes
    imagenes = actualizar_imagenes(nuevo_canvas(perio))

    return render_template('perio.html', tmp=id_perio,
        dict=dict_perio, primer_diente=primer_diente,
        imagenes=imagenes)

@socketio.on('update_perio')
def update_perio(data):
    '''Recibe datos, devuelve la nueva imagen procesada en base64'''
    # Lee el tmp
    perio = Guardar.file_to_perio(data['tmp'],
                id_usuario = session['usuario'],
                silent = True)

    # Actualiza los datos
    filtro = set()
    respuesta = {}

    for num, datos in data.items():
        if not num.isnumeric():
            continue

        for titulo, valor in datos.items():
            # Si alguno de los datos cambiados tiene un efecto
            # en las imágenes y hay que actualizarlas
            filtrar = 'sup' if perio[num]['superior'] else 'inf'
            if titulo.replace('_', '') in [ 'SANGRADO', 'LMG', 'SONDAJE', 'MARGEN' ]:
                filtrar = 'sup' if perio[num]['superior'] else 'inf'
                filtrar += '_b' if '_' in titulo else '_a'
                filtro.add(filtrar)

            elif titulo in [ 'IMPLANTE', 'FURCA', 'atributos' ]:
                filtro.add(filtrar + '_a')
                filtro.add(filtrar + '_b')

            if titulo == 'atributos':
                perio[num]['atributos'] = valor
            else:
                perio[num]['valores'][titulo] = valor

            # Actualiza el NI y si cambió lo agrega a la respuesta
            if titulo.replace('_', '') in [ 'SONDAJE', 'MARGEN' ]:
                perio[num].calcular_ni()
                ni = ('_' if '_' in titulo else '') + 'NI'
                if perio[num]['valores'][ni] is not None:
                    respuesta['{}-{}'.format(ni, num)] = ' '.join(map(str, perio[num]['valores'][ni]))

    # Guarda el tmp
    Guardar.perio_to_file(perio,
                archivo = data['tmp'],
                id_usuario = session['usuario'],
                silent = True)

    # Obtiene los str de las imágenes actualizadas
    if len(filtro) > 0:
        respuesta.update( actualizar_imagenes(nuevo_canvas(perio, filtro=filtro)) )

    # Devuelve los datos
    emit('response_perio', respuesta)


@app.route('/eliminar_perio')
def eliminar_perio():
    '''Elimina el perio de la carpeta del usuario'''

    usuario = int(request.args.get('u'))
    id_perio = request.args.get('p')

    if usuario == session['usuario']:
        Guardar.eliminar_perio(usuario, id_perio)

    return redirect(url_for('.index'))

def login_user(user: Usuario, contrasena = None):
    result = None

    if user.get('id_usuario'):
        if contrasena is None:
            # Viene de la página de Registro
            result = True
        else:
            # Viene de la página de Login
            result = user.comprobar_contrasena(contrasena)

        if result:
            # Login user
            session['usuario'] = user['id_usuario']

    # En este punto:
    # -> Si result es True se inició la sesión
    # -> Si result es False es que la contraseña es inválida
    # -> Si existe user['error'] es que ocurrió un error y devuelve el mensaje
    return user.get('error', result)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Verifica que esté loggeado
    if 'usuario' in session:
        return redirect(url_for('.index'))

    result = None

    if request.method == 'POST':
        email = request.values.get('email')
        contrasena = request.values.get('key')
        result = login_user( Usuario(email=email), contrasena )

    return render_template('login.html', result=result)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    datos = {}
    result = None

    if request.method == 'POST':
        datos.update(request.values)
        datos['suscripcion'] = datos.get('suscripcion', 'off')
        result = login_user( Usuario(nuevousuario=datos) )

    return render_template('registro.html', result=result, datos=datos)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return render_template('login.html', logout=True)

@socketio.on('update_time')
def update_time(readonly):
    '''Es llamado cada segundo desde JS, si es necesario descuenta un crédito,
        y devuelve la hora y la cantidad de créditos que tiene restantes'''

    try:
        # Obtiene la hora actual en Colombia
        tz = pytz.timezone('America/Bogota')
        hora = datetime.now(tz)

        # Si es un nuevo minuto (segundos == 0), descuenta un crédito
        cobrar = hora.second == 0 and not readonly

        # Obtiene la cantidad actualizada de créditos
        usuario = Usuario(id_usuario=session['usuario'])
        creditos = usuario.obtener_creditos(cobrar)

        if creditos == 0:
            emit('redirect', {'url': url_for('creditos')})

        horas_restantes = creditos//60
        if horas_restantes > 0:
            horas_restantes = f'{horas_restantes} hora{"" if horas_restantes == 1 else "s"} y '
        else:
            horas_restantes = ''

        minutos_restantes = creditos%60
        minutos_restantes = f'{minutos_restantes} minuto{"" if minutos_restantes == 1 else "s"}'

        respuesta = {
            'usuario': usuario['usuarios']['email'],
            'cred': f'{creditos:,}'.replace(',', '.'),
            'cred-tiempo': f'Restan {horas_restantes}{minutos_restantes}',
            'hora': format_datetime(hora,
                                    "h:mm:ss a, EEEE dd 'de' MMMM 'de' YYYY",
                                    locale='es_CO')
        }

        # Devuelve los datos
        emit('response_time', respuesta)
    except Exception as ex:
        Log.out(f'id_usuario {session.get("usuario")}: {ex}',
                'error', silent=False, origen='app.update_time')

def consultar_creditos():
    '''Consulta los créditos en la BD'''
    # Verifica que esté loggeado
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = Usuario(id_usuario=session['usuario'])
    # Obtiene la cantidad actualizada de créditos
    creditos = usuario.obtener_creditos(False)

    return creditos, usuario

@app.route('/creditos', methods=['GET', 'POST'])
def creditos():
    '''Muestra créditos actuales, botón de pago, e historial de transacciones'''
    tmp = request.values.get('tmp')

    creditos, usuario = consultar_creditos()
    # Obtiene el historial de transacciones
    transacciones = usuario.obtener_transacciones()

    return render_template('creditos.html', tmp=tmp, creditos=creditos,
                            transacciones=transacciones,
                            email=usuario['usuarios']['email'],
                            valor_credito=valor_credito)

@socketio.on('checkout')
def checkout(datos):
    '''Utiliza la API para cobrar un pago'''

    # Obtiene los datos del formulario
    email = datos.get('email')
    monto = datos.get('monto')
    tiempo = datos.get('tiempo')

    # Crea un ítem en la preferencia
    preference_data = {
        'items': [
            {
                'title': f'Acceso a iPerio.com por{tiempo}',
                'quantity': 1,
                'unit_price': int(monto),
            }
        ],
        'back_urls': {
            'failure': url_for("confirmacion_pago", _external=True),
            'pending': url_for("confirmacion_pago", _external=True),
            'success': url_for("confirmacion_pago", _external=True),
        },
        'notification_url': '' if app.debug else url_for("confirmacion_pago", _external=True),
        'payer': {
            'email': email
        },
        'auto_return': 'all',
        'external_reference': session.get('usuario')
    }

    preference_response = mp_sdk.preference().create(preference_data)
    preference = preference_response['response']

    emit('mercadopago', {
        'public_key': mp_public_key,
        'preference_id': preference.get('id')
    })


@app.route('/confirmacion', methods=['GET', 'POST'])
def confirmacion_pago():
    '''Recibe el resultado del pago y actualiza la BD, y muestra el estado del pago'''

    if request.method == 'POST':
        # Recibida desde Instant Payments Notifications IPN
        codigo = request.values.get('id')
    else:
        # El cliente es redirigido desde la pasarela
        codigo = request.args.get('payment_id')

    headers = { 'Authorization': f'Bearer {mp_access_token}' }
    response = requests.get(
                        f'https://api.mercadopago.com/v1/payments/{codigo}',
                        headers=headers
                        )
    response = response.json()

    id_usuario = response['external_reference']
    usuario = Usuario(id_usuario=id_usuario)
    usuario.registrar_pago(
                        transaccion = codigo,
                        fecha_transaccion = response['date_created'],
                        estado = response['status'],
                        detalle_estado = response['status_detail'],
                        tipo_pago = response['payment_type_id'],
                        metodo_pago = response['payment_method_id'],
                        monto = response['transaction_amount']
                        )

    return redirect(url_for('creditos'))
