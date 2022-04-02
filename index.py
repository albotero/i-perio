#!/usr/bin/python3

from flask import Flask, render_template
from flask import jsonify, request
from flask import current_app

from scripts.diente import Diente, get_titulos
from scripts.grafico import nuevo_canvas
from scripts.guardar_perio import Guardar
from scripts.main import nuevo_perio
from scripts.process_images import actualizar_imagenes

import os
import uuid

'''# Para test
import cv2
import random as rd'''

app = Flask(__name__)
os.chdir(os.path.dirname(__file__))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/perio')
def perio():
    # Declaración de variables
    perio = nuevo_perio()
    '''# Perio de prueba
    perio = test_grafico()'''
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

@app.route('/update_perio', methods=['POST'])
def update_perio():
    '''Recibe POST con datos, devuelve la nueva imagen procesada en base64'''
    data = request.get_json()
    # Lee el tmp
    perio = Guardar.file_to_perio(data['tmp'], silent = True)
    # Actualiza los datos
    filtro = set()
    for num, datos in data.items():
        if not num.isnumeric():
            continue
        for titulo, valor in datos.items():
            perio[num]['valores'][titulo] = valor
            filtro.add('sup' if perio[num]['superior'] else 'inf')
    # Guarda el tmp
    Guardar.perio_to_file(perio, data['tmp'], silent = True)
    # Obtiene los str de las imágenes actualizadas
    imagenes = actualizar_imagenes(nuevo_canvas(perio, filtro=filtro))
    # Devuelve las imagenes
    return imagenes

'''def test_grafico():
    # Crea nuevo perio
    perio = nuevo_perio()

    for num, diente in perio.items():
        if type(num) is not int:
            continue

        diente['atributos'] = Diente._atributos[num % 4]

        if num % 3 == 0 and diente['atributos'] != 'Ausente':
            diente['valores']['IMPLANTE'] = 'Si'

        # Datos aleatorios
        for opt in ['', '_']:
            diente['valores'][opt + 'MARGEN'] = \
                rd.randint(-3, 1), rd.randint(-3, 1), rd.randint(-3, 1)
            diente['valores'][opt + 'SONDAJE'] = \
                rd.randint(0, 7), rd.randint(0, 7), rd.randint(0, 7)
            diente['valores'][opt +'SANGRADO'] = \
                not rd.getrandbits(1), not rd.getrandbits(1), not rd.getrandbits(1)
            diente['valores'][opt +'SUPURACIÓN'] = \
                not rd.getrandbits(1), not rd.getrandbits(1), not rd.getrandbits(1)

        # Algunos dientes no se les especifica LMG
        diente['valores']['L.M.G'] = str(rd.randint(6,10))
        # Genera las _LMG de los dientes inferiores
        if not diente['superior']:
            diente['valores']['_L.M.G'] = str(rd.randint(6,10))

        diente.calcular_ni()

    # Devuelve el canvas para mostrarlo en el ejemplo en index.html
    return perio'''
