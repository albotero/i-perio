#!/usr/bin/python3

from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit

from scripts.diente import Diente, get_titulos
from scripts.grafico import nuevo_canvas
from scripts.guardar_perio import Guardar
from scripts.log import Log
from scripts.main import nuevo_perio
from scripts.process_images import actualizar_imagenes
from scripts.usuarios import valor_credito, ejecutar_mysql, Usuario

from datetime import datetime
from babel.dates import format_datetime
import pytz

import os
import uuid

app = Flask(__name__, instance_relative_config = True)
app.secret_key = 'perio'

socketio = SocketIO(app, cors_allowed_origins = '*', async_mode='gevent') #, logger=True, engineio_logger=True)

os.chdir(os.path.dirname(__file__))

@app.route('/', methods=['GET', 'POST'])
def perio():
    # Verifica que esté loggeado
    if 'usuario' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Carga un perio existente
        filename = request.values.get('tmp')
        try:
            perio = Guardar.file_to_perio(filename, silent = True)
        except:
            perio = nuevo_perio()
    else:
        # Genera un archivo temporal para guardar el perio
        filename = uuid.uuid4().hex
        perio = nuevo_perio()

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
        if type(num) is not int:
            continue
        # Si hace parte del perio superior o del inferior
        grupo = 'sup' if diente['superior'] else 'inf'
        dict_perio[grupo][num] = diente

    # Obtiene los str de las imágenes
    imagenes = actualizar_imagenes(nuevo_canvas(perio))

    Guardar.perio_to_file(perio,
                archivo = filename,
                id_usuario = session['usuario'],
                silent = True)

    return render_template('perio.html', tmp=filename,
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

@app.route('/logout')
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

@app.route('/creditos', methods=['GET', 'POST'])
def creditos():
    '''Muestra créditos actuales, botón de pago, e historial de transacciones'''
    tmp = request.values.get('tmp')

    # Verifica que esté loggeado
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = Usuario(id_usuario=session['usuario'])
    # Obtiene la cantidad actualizada de créditos
    creditos = usuario.obtener_creditos(False)
    # Obtiene el historial de transacciones
    transacciones = usuario.obtener_transacciones()

    return render_template('creditos.html', tmp=tmp, creditos=creditos,
                            transacciones=transacciones,
                            email=usuario['usuarios']['email'],
                            valor_credito=valor_credito)

@app.route('/checkout', methods=['POST'])
def checkout():
    '''Utiliza la API para cobrar un pago'''
    comando = f'''
        SELECT MAX(`transaccion`) as MAX
        FROM `creditos`
        WHERE `transaccion` != "gastos";
        '''
    _, prev_cups, _ = ejecutar_mysql(comando, origen='app.checkout')
    if len(prev_cups) == 0:
        prev_cups = 0
    else:
        prev_cups = int(prev_cups[0].get('MAX')[3:])
    nuevo_cups = f'CUP{prev_cups + 1:05}'
    return nuevo_cups;


@app.route('/confirmacion')
def confirmacion_pago():
    '''Recibe el resultado del pago, actualiza la BD, y muestra el estado del pago'''
    pass
