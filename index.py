#!/usr/bin/python3

from flask import Flask, render_template

from scripts.diente import Diente
from scripts.grafico import nuevo_canvas
from scripts.main import nuevo_perio

import cv2
import random as rd

from PIL import Image
import io
import numpy as np
import base64

app = Flask(__name__)

@app.route('/')
def index():
    canvas = test_grafico()
    for key in canvas.keys():
        try:
            canvas[key] = frame(canvas[key])
        except Exception as ex:
            print(ex)
    return render_template('index.html', **canvas)

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
    #return render_template("main.html", image=uri)
    return uri

def test_grafico():
    # Crea nuevo perio
    perio = nuevo_perio()

    for num, diente in perio.items():
        if type(num) is not int:
            continue

        '''# Todos los dientes con mismo margen y sondaje
        margen = '0 0 0'
        sondaje = '1 1 1'
        diente['valores']['MARGEN'] = margen
        diente['valores']['_MARGEN'] = margen
        diente['valores']['SONDAJE'] = sondaje
        diente['valores']['_SONDAJE'] = sondaje
        continue'''

        diente['atributos'] = Diente._atributos[num % 4]

        if num % 3 == 0:
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

    # Obtiene las 4 imágenes del perio
    canvas = nuevo_canvas(perio)

    # Muestra las imagenes generadas
    '''for area, imagen in canvas.items():
        cv2.imshow(area, imagen[0])
    cv2.waitKey(0)
    cv2.destroyAllWindows()'''

    # Devuelve el canvas para mostrarlo en el ejemplo en index.html
    return canvas
