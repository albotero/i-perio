#!/usr/bin/env python3

from diente import Diente
from process_images import color, coord, process_fill, read_transparent
import cv2
import numpy as np

class NuevoDiente(object):

    img_original = None
    img_procesada = None
    diente = None
    espacio = 0
    area = None

    def __init__(self, diente, src, area, espacio):
        '''Inicializa un objeto NuevoDiente con la imagen original y la imagen sin alpha'''
        self.area = area
        self.diente = diente
        self.espacio = espacio
        self.img_original = cv2.imread(src)
        self.img_procesada = read_transparent(src)
        # Define las coordenadas de las cuadrículas
        self.diente['coordenadas'] = coord(self.img_original, espacio = espacio)

    def get(self):
        '''Devuelve la imagen procesada'''
        return self.img_procesada

    def pintar_ausente(self):
        '''Pinta de negro si el diente tiene el atributo Ausente'''
        if self.diente['atributos'] == 'Ausente':
            self = process_fill(self.img_original, self.img_procesada)

    def obtener_coordenadas(self, valores_y, indices_x, base = [0,0,0]):
        '''Obtiene las coordenadas de cada punto de la línea

        Índices x posibles:
         0: borde izquierdo de la imagen
         1: borde izquierdo del diente
         2: centro del diente
         3: borde derecho del diente
         4: borde derecho de la imagen'''

        # Define la línea 0 donde empieza la cuadrícula
        linea_0 = 98 if self.diente['superior'] else 49

        valores_y = [int(x) for x in valores_y]
        puntos = []
        for i in range(3):
            if self.diente['superior']:
                indice = linea_0 - valores_y[i] * self.espacio
                y = indice - base[i]
            else:
                indice = linea_0 + valores_y[i] * self.espacio
                y = indice + base[i]
            x = self.diente['coordenadas'][indice][indices_x[i]]
            puntos += [[x, y]]

        return np.array(puntos, np.int32)

    def dibujar_cuadriculas(self):
        '''Dibuja las líneas entre la corona y la raíz'''
        for y, x in self.diente['coordenadas'].items():
            # No dibuja nada en la corona
            if self.diente['superior'] and y > 98:
                continue
            if not self.diente['superior'] and y < 49:
                continue
            # Dibuja la línea
            self.img_procesada = cv2.line(
                self.img_procesada,
                (x[0], y), (x[-1], y),
                color['gris'], 1)

    def recta_to_curva(self, puntos):
        '''Suaviza las líneas para que los ángulos sean curvos'''
        tension = 1
        n = 32
        # Duplicate first and last points
        _pts = puntos.tolist()
        _pts = [_pts[0]] + _pts + [_pts[1]]
        # Create new list and append curve points
        res = []
        for i in range(1, len(_pts) - 2):
            for t in range(n):
                # Calc tension vectors
                t1x = (_pts[i][0] - _pts[i - 1][0]) * tension
                t2x = (_pts[i + 1][0] - _pts[i][0]) * tension

                t1y = (_pts[i][1] - _pts[i - 1][1]) * tension
                t2y = (_pts[i + 1][1] - _pts[i][1]) * tension

                # Calc step
                st = t / n

                # Calc cardinals
                c1 = 2 * (st ** 3) - 3 * (st ** 2) + 1
                c2 = -(2 * (st ** 3)) + 3 * (st ** 2)
                c3 = (st ** 3) - 2 * (st ** 2) + st
                c4 = (st ** 3) - (st ** 2)

                # Calc x and y cords with common control vectors
                x = c1 * _pts[i][0] + c2 * _pts[i + 1][0] + c3 * t1x + c4 * t2x
                y = c1 * _pts[i][1] + c2 * _pts[i + 1][1] + c3 * t1y + c4 * t2y

                res.append([x, y])

        return [np.array(res, np.int32)]

    def dibujar_curvas(self, dato):
        '''Dibuja las curvas de sondaje, margen y LMG'''

        opt = '_' if self.area == '_b' else ''

        color_linea = color['negro']
        if dato == 'margen':
            color_linea = color['rojo']
            dato = opt + 'MARGEN'
        elif dato == 'lmg' and self.diente['superior'] and self.area == '_b':
            # Los dientes superiores no tienen _L.M.G
            return
        elif dato == 'lmg':
            color_linea = color['verde']
            dato = opt + 'L.M.G'
        else:
            dato = opt + 'SONDAJE'

        # Obtiene los puntos de la linea
        valores = self.diente['valores'][dato]
        if valores is not None:
            valores = valores.strip().split()
            if dato == opt + 'SONDAJE':
                offset = [int(x) for x in self.diente['valores'][opt + 'MARGEN'].split()]
                coord = self.obtener_coordenadas(valores, [1,2,3], offset)
            else:
                coord = self.obtener_coordenadas(valores, [1,2,3])
            cv2.polylines(
                self.img_procesada, self.recta_to_curva(coord),
                isClosed = False, color = color_linea,
                thickness = 2, lineType = cv2.LINE_AA)


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
            espacio = 7
            src = 'img/dientes/{}{}.png'.format(num, s)
            canv_area = 'sup' if diente['superior'] else 'inf'
            # Carga la imagen del diente
            nuevo_diente = NuevoDiente(diente, src, s, espacio)
            # Si el diente está ausente, lo pinta de negro
            nuevo_diente.pintar_ausente()
            # Pinta las bolsas y pseudobolsas
            # Dibuja las líneas correspondientes
            nuevo_diente.dibujar_cuadriculas()
            nuevo_diente.dibujar_curvas('margen')
            nuevo_diente.dibujar_curvas('sondaje')
            nuevo_diente.dibujar_curvas('lmg')
            # Agrega la imagen del diente al canvas
            canvas[canv_area + s] = stack_diente(canvas.get(canv_area + s), nuevo_diente.get())

    return canvas
