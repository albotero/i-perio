#!/usr/bin/env python3

from diente import Diente
from diente_csv import coord
from process_images import color, process_fill, read_transparent
import cv2
import numpy as np

class NuevoDiente(object):

    img_original = None
    img_procesada = None
    diente = None
    espacio = 0
    area = None
    top = 0

    def __init__(self, diente, src, area, espacio):
        '''Inicializa un objeto NuevoDiente con la imagen original y la imagen sin alpha'''
        self.area = area
        self.diente = diente
        self.espacio = espacio
        self.img_original = cv2.imread(src)
        self.img_procesada = read_transparent(src)
        # Si el diente está ausente, lo pinta de negro
        self.pintar_ausente()
        # Define las coordenadas de las cuadrículas
        _, width, _ = self.img_procesada.shape
        self.top, self.diente['coordenadas'] = coord(diente['diente'], area, width, espacio)
        self.img_procesada = self.espacio_superior(self.top, self.img_procesada, self.diente['diente'])
        #self.diente['coordenadas'] = coord(self.img_original, espacio = espacio)

    def get(self):
        '''Devuelve la imagen procesada'''
        return self.img_procesada

    def pintar_ausente(self):
        '''Pinta de negro si el diente tiene el atributo Ausente'''
        if self.diente['atributos'] == 'Ausente':
            img = self.espacio_superior(self.top, self.img_original, self.diente['diente'])
            self = process_fill(img, self.img_procesada)

    def espacio_superior(self, top, img, num_diente):
        new_img = cv2.copyMakeBorder(img, top, 0, 0, 0, cv2.BORDER_CONSTANT, value=color['blanco'])
        return new_img

    def obtener_coordenadas(self, valores_y, indices_x):
        '''Obtiene las coordenadas de cada punto de la línea

        Índices x posibles:
         0: borde izquierdo de la imagen
         1: borde izquierdo del diente
         2: centro del diente
         3: borde derecho del diente
         4: borde derecho de la imagen'''

        # Define la línea 0 donde empieza la cuadrícula
        linea_0 = 98 if self.diente['superior'] else 49

        puntos = []
        for i in range(3):
            if self.diente['superior']:
                y = linea_0 - valores_y[i] * self.espacio
            else:
                y = linea_0 + valores_y[i] * self.espacio

            # Gets x coord else set defaults
            if y in self.diente['coordenadas'].keys():
                x = self.diente['coordenadas'][y][indices_x[i]]
            else:
                height, width, channels = self.img_original.shape
                x = width / 4 * indices_x[i]
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
            valores = [int(x) for x in valores.split()]
            if dato == opt + 'SONDAJE':
                # La base de sondaje es la línea de Margen
                offset = [int(x) for x in self.diente['valores'][opt + 'MARGEN'].split()]
                valores = [valores[x] + offset[x] for x in range(3)]
                coord = self.obtener_coordenadas(valores, [1,2,3])
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
    x, y, _ = diente.shape
    canvas_x, canvas_y, _ = canvas.shape
    nuevo_diente = cv2.resize(diente, (int(y*float(canvas_x)/x), canvas_x))

    # Devuelve la imagen resultante
    return np.concatenate((canvas, nuevo_diente), axis = 1)

def dibujar_cuadriculas(img, arcada, area, espacio):
    '''Dibuja las líneas entre la corona y la raíz'''
    # Define y_inicial y y_final para no dibujar sobre la corona
    y_inicial = 0 if arcada == 'sup' else 56
    y_final = 105 if arcada == 'sup' else 200
    _, width, _ = img.shape

    for y in range(3, 25 * espacio, espacio):
        if y >= y_inicial and y <= y_final:
            # Dibuja la línea
            img = cv2.line(img, (0, y), (width, y), color['gris'], 1)

    return img

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
            canvas[canv_area + s] = stack_diente(canvas.get(canv_area + s), nuevo_diente.get())

    for arcada in ['sup', 'inf']:
        for area in ['_a', '_b']:
            canvas[arcada + area] = dibujar_cuadriculas(canvas[arcada + area], arcada, area, espacio)

    return canvas
