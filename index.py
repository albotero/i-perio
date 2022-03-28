#!/usr/bin/python3

from flask import Flask, render_template
from flask import jsonify, request
from flask import current_app

from scripts.diente import Diente, get_titulos
from scripts.grafico import nuevo_canvas
from scripts.main import nuevo_perio

import cv2
import random as rd

from PIL import Image
import io
import numpy as np
import base64
import os

app = Flask(__name__)

def frame(arr: np.ndarray):
    # Reverse colors BGR to RGB
    arr = arr[:,:,::-1]
    # Gets base64
    mem_bytes = io.BytesIO()
    img = Image.fromarray(arr)
    img.save(mem_bytes, 'JPEG')
    mem_bytes.seek(0)
    img_base64 = base64.b64encode(mem_bytes.getvalue()).decode('ascii')
    mime = "image/jpeg"
    uri = "data:%s;base64,%s"%(mime, img_base64)
    return uri

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/perio')
def perio():
    if not current_app.debug:
        os.chdir('/home/alejandro/i-perio')
    perio = nuevo_perio()
    dict_perio = { 'sup': {}, 'inf': {} }

    primer_diente = [18, 28, 38, 48]

    for d in primer_diente:
        diente = Diente(d)
        grupo = 'sup' if diente['superior'] else 'inf'
        dict_perio[grupo]['titulos'] = get_titulos(diente)

    for num, diente in perio.items():
        if type(num) is not int:
            continue
        # Si hace parte del perio superior o del inferior
        grupo = 'sup' if diente['superior'] else 'inf'
        # Agrega el título del diente
        dict_perio[grupo][num] = diente

    return render_template('perio.html', dict=dict_perio, primer_diente=primer_diente)

@app.route('/update_perio', methods=['POST'])
def update_perio():
    '''Recibe POST con datos, devuelve la nueva imagen procesada en base64'''
    data = request.get_json()

    # Test data
    data = test_grafico()
    for key in data.keys():
        try:
            data[key] = frame(data[key])
        except Exception as ex:
            print(ex)

    return jsonify(data)

def test_grafico():
    # Crea nuevo perio
    perio = nuevo_perio()

    for num, diente in perio.items():
        if type(num) is not int:
            continue

        diente['atributos'] = Diente._atributos[num % 4]

        if num % 3 == 0 and diente['atributos'] != 'Ausente':
            diente['valores']['IMPLANTE'] = True

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
    return nuevo_canvas(perio)
