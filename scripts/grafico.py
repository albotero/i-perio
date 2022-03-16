#!/usr/bin/env python3

from process_images import process_fill
import cv2

def nuevo_canvas():
    pass

def dibujar_diente():
    pass

def relleno_diente(src, color = 'negro'):
    '''Obtiene la imagen del diente con el relleno 'color' especificado'''
    img = process_fill(src, color)

    # Por el momento muestra la imagen, luego la pasa al canvas
    cv2.imshow(src, img)
    cv2.waitKey(2000)
    cv2.destroyAllWindows()

def dibujar_linea(color, grosor, limite_diente):
    pass

relleno_diente('img/dientes/24b.png')
