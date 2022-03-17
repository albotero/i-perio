#!/usr/bin/env python3

from diente import Diente
from process_images import process_fill, read_transparent
import cv2
import numpy as np

def dibujar_lineas(diente):
    '''Según diente['valores'] dibuja las líneas que correspondan'''
    # Pendiente implementar
    return diente

def stack_diente(canvas, diente):
    '''Apila horizontalmente el diente nuevo en el canvas actual'''
    # Si es la primer imagen del canvas, devuelve el canvas
    if canvas is None:
        return diente

    # Ajusta el tamaño de la nueva imagen
    #diente = diente[:,:,:3]
    x, y, _ = diente.shape
    canvas_x, canvas_y, _ = canvas.shape
    nuevo_diente = cv2.resize(diente, (int(y*float(canvas_x)/x), canvas_x))

    # Devuelve la imagen resultante
    return np.concatenate((canvas, nuevo_diente), axis = 1)


def nuevo_canvas(perio):
    '''Crea los 4 canvas con las imágenes de los dientes'''
    canvas = {}

    for num, diente in perio.items():
        if type(diente) is not Diente:
            # Si no es un diente no hace nada
            continue

        if perio['pediatrico']:
            num -= 40

        for s in ['_a', '_b']:
            # Carga la imagen del diente
            src = 'img/dientes/{}{}.png'.format(num, s)
            nuevo_diente = read_transparent(src)
            # Si el diente está ausente, lo pinta de negro
            if perio[num]['atributos'] == 'Ausente':
                nuevo_diente = process_fill(src, nuevo_diente)
            # Dibuja las líneas que correspondan
            nuevo_diente = dibujar_lineas(nuevo_diente)
            # Agrega la imagen del diente al canvas
            area = 'sup' if num < 30 else 'inf'
            canvas[area + s] = stack_diente(canvas.get(area + s), nuevo_diente)

    return canvas
