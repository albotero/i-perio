#!/usr/bin/python3

from flask import Flask, render_template
from flask import request
from flask import current_app
from flask_socketio import SocketIO, emit

from scripts.diente import Diente, get_titulos
from scripts.grafico import nuevo_canvas
from scripts.guardar_perio import Guardar
from scripts.main import nuevo_perio
from scripts.process_images import actualizar_imagenes

import os
import uuid

app = Flask(__name__, instance_relative_config = True)
app.secret_key = 'perio'
socketio = SocketIO(app, cors_allowed_origins = '*', async_mode='gevent', logger=True, engineio_logger=True)

os.chdir(os.path.dirname(__file__))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/perio')
def perio():
    # Declaración de variables
    perio = nuevo_perio()
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

    # Genera un archivo temporal para guardar el perio
    filename = uuid.uuid4().hex
    Guardar.perio_to_file(perio, filename, silent = True)

    return render_template('perio.html', tmp=filename, dict=dict_perio,
        primer_diente=primer_diente, imagenes=imagenes)

@socketio.on("update_perio")
def update_perio(data):
    '''Recibe datos, devuelve la nueva imagen procesada en base64'''
    # Lee el tmp
    perio = Guardar.file_to_perio(data['tmp'], silent = True)
    # Actualiza los datos
    filtro = set()
    for num, datos in data.items():
        if not num.isnumeric():
            continue
        for titulo, valor in datos.items():
            # Si alguno de los datos cambiados tiene un efecto
            # en las imágenes y hay que actualizarlas
            filtrar = 'sup' if perio[num]['superior'] else 'inf'
            if titulo.replace('_', '') in [ 'SANGRADO', 'SUPURACIÓN', 'L.M.G', 'SONDAJE', 'MARGEN' ]:
                actualizar = True
                filtrar = 'sup' if perio[num]['superior'] else 'inf'
                filtrar += '_b' if '_' in titulo else '_a'
                filtro.add(filtrar)
            elif titulo in [ 'IMPLANTE', 'atributos' ]:
                actualizar = True
                filtro.add(filtrar + '_a')
                filtro.add(filtrar + '_b')

            if titulo == 'atributos':
                perio[num]['atributos'] = valor
            else:
                perio[num]['valores'][titulo] = valor

    # Guarda el tmp
    Guardar.perio_to_file(perio, data['tmp'], silent = True)
    # Obtiene los str de las imágenes actualizadas
    if len(filtro) > 0:
        imagenes = actualizar_imagenes(nuevo_canvas(perio, filtro=filtro))
        # Devuelve las imagenes
        emit('response_perio', imagenes)