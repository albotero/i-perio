#!/usr/bin/env python3

from diente import Diente
from diente_csv import coord
from process_images import color, process_fill, read_transparent
import cv2
import numpy as np

class NuevoDiente(object):

    img_original, img_procesada = None, None
    diente, area = None, None
    espacio, linea_0, top = 0, 0, 0
    height = 160

    def get(self):
        '''Devuelve la imagen procesada'''
        return self.img_procesada

    def bordes(self):
        '''Alinea el diente con la cuadrícula añadiendo un espacio en la parte superior
        y añade un borde en la parte inferior para que la imagen sea de 140px'''
        y, x, _ = self.img_procesada.shape
        bottom = self.height - (self.top + y)

        self.img_procesada = cv2.copyMakeBorder(
            self.img_procesada, self.top, bottom, 0, 0,
            cv2.BORDER_CONSTANT, value=color['blanco'])

        # Temporalmente coloca un borde verde a la izquierda para poder medir las
        # coordenadas de los dientes
        self.img_procesada = cv2.copyMakeBorder(
            self.img_procesada, 0, 0, 1, 0,
            cv2.BORDER_CONSTANT, value=color['verde'])

    def pintar_ausente(self):
        '''Pinta de negro si el diente tiene el atributo Ausente'''
        if self.diente['atributos'] == 'Ausente':
            self.img_procesada = process_fill(self.img_original, self.img_procesada)

    def dibujar_cuadriculas(self):
        '''Dibuja las líneas entre la corona y la raíz'''
        # Define y_inicial y y_final para no dibujar sobre la corona
        if self.diente['superior']:
            y_inicial = 1 if self.area == '_a' else 5
            y_final = 105
        else:
            y_inicial = 51 if self.area == '_a' else 50
            y_final = 200
        _, width, _ = self.img_procesada.shape

        # Temporalmente hace que toda la imagen tenga cuadrículas para poder medir
        # las coordenadas de los dientes
        y_inicial = 0
        y_final = 200

        for y in range(y_inicial, y_final + 1, self.espacio):
            # Dibuja la línea
            self.img_procesada = cv2.line(self.img_procesada, (0, y), (width, y), color['gris'], 1)

        return self.img_procesada

    def obtener_coordenadas(self, valores_y):
        '''Obtiene las coordenadas de cada punto de la línea

        Índices x posibles:
         0: borde izquierdo de la imagen
         1: borde izquierdo del diente
         2: centro del diente
         3: borde derecho del diente
         4: borde derecho de la imagen'''

        puntos = []
        for i in range(3):
            if self.diente['superior']:
                y = self.linea_0 - valores_y[i] * self.espacio
            else:
                y = self.linea_0 + valores_y[i] * self.espacio

            # X coordinate
            height, width, channels = self.img_original.shape
            x = self.diente['coordenadas'].get(y,[0,width / 2,width])[i]

            puntos += [[x, y]]

        return np.array(puntos, np.int32)

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
            valores = [int(y) for y in valores.split()]
            if dato == opt + 'SONDAJE':
                # La base de sondaje es la línea de Margen
                offset = [int(y) for y in self.diente['valores'][opt + 'MARGEN'].split()]
                valores = [valores[x] + offset[x] for x in range(3)]
                coord = self.obtener_coordenadas(valores)
            else:
                coord = self.obtener_coordenadas(valores)
            cv2.polylines(
                self.img_procesada, self.recta_to_curva(coord),
                isClosed = False, color = color_linea,
                thickness = 2, lineType = cv2.LINE_AA)

    def __init__(self, diente, src, area, espacio):
        '''Inicializa un objeto NuevoDiente con la imagen original y la imagen sin alpha'''
        self.area = area
        self.diente = diente
        self.espacio = espacio
        self.img_original = cv2.imread(src)
        self.img_procesada = read_transparent(src)
        # Define las coordenadas de las cuadrículas
        _, width, _ = self.img_procesada.shape
        self.top, self.diente['coordenadas'] = coord(diente['diente'], area, width, espacio)
        # Agrega el borde superior a la imagenes
        self.bordes()
        # Si el diente está ausente, lo pinta de negro
        self.pintar_ausente()
        # Dibuja las cuadrículas
        self.dibujar_cuadriculas()


def stack_diente(canvas, diente):
    '''Apila horizontalmente el diente nuevo en el canvas actual'''
    # Obtiene la imagen procesada
    nuevo_diente = diente.get()
    # Si es la primer imagen del canvas, devuelve el canvas
    if canvas is None:
        return nuevo_diente
    # Devuelve la imagen resultante
    return np.concatenate((canvas, nuevo_diente), axis = 1)

def nuevo_canvas(perio):
    '''Crea los 4 canvas con las imágenes de los dientes'''
    canvas = {}
    espacio = 7

    for num, diente in perio.items():
        if type(diente) is not Diente:
            # Si no es un diente no hace nada
            continue

        if perio['pediatrico']:
            num -= 40

        for s in ['_a', '_b']:
            src = 'img/dientes/{}{}.png'.format(num, s)
            canv_area = 'sup' if diente['superior'] else 'inf'
            # Carga la imagen del diente
            nuevo_diente = NuevoDiente(diente, src, s, espacio)
            # Pinta las bolsas y pseudobolsas
            # Dibuja las líneas correspondientes
            nuevo_diente.dibujar_curvas('margen')
            nuevo_diente.dibujar_curvas('sondaje')
            nuevo_diente.dibujar_curvas('lmg')
            # Agrega la imagen del diente al canvas
            canvas[canv_area + s] = stack_diente(canvas.get(canv_area + s), nuevo_diente)

    return canvas
