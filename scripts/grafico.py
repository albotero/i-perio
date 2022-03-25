#!/usr/bin/env python3

from diente import Diente
from diente_csv import coord
from process_images import color, process_fill, read_transparent
import cv2
import numpy as np

class NuevoDiente(object):
    height = 160

    def get(self):
        '''Devuelve la imagen procesada'''
        return self.img_procesada

    def bordes(self, img):
        '''Alinea el diente con la cuadrícula añadiendo un espacio en la parte superior
        y añade un borde en la parte inferior para que la imagen sea de 140px'''
        y, x, _ = img.shape
        self.bottom = self.height - (self.top + y)

        return cv2.copyMakeBorder(img, self.top, self.bottom, 0, 0,
            cv2.BORDER_CONSTANT, value=color['blanco'])

    def pintar_ausente(self, img):
        '''Pinta de negro si el diente tiene el atributo Ausente'''
        if self.diente['atributos'] == 'Ausente':
            img = process_fill(self.img_original, img)
        return img

    def limite_vertical(self):
        '''Define y_inicial y y_final para no dibujar sobre la corona'''
        if self.diente['superior']:
            y_inicial = 1 if self.area == '_a' else 5
            y_final = 101 if self.area == '_a' else 105
        else:
            y_inicial = 51 if self.area == '_a' else 50
            y_final = 200
        return y_inicial, y_final

    def dibujar_cuadriculas(self):
        '''Dibuja las líneas entre la corona y la raíz'''
        _, width, _ = self.img_procesada.shape

        for y in range(self.y_inicial, self.y_final + 1, self.espacio):
            # Dibuja la línea
            self.img_procesada = cv2.line(self.img_procesada, (0, y), (width, y), color['gris'], 1)

        return self.img_procesada

    def obtener_coordenadas(self, valores_y):
        '''Obtiene las coordenadas de cada punto de la línea

        Índices x:
         0: borde izquierdo del diente
         1: centro del diente
         2: borde derecho del diente'''

        puntos = []

        for i in range(3):
            if self.diente['superior']:
                y = int(self.y_final/self.espacio) - valores_y[i]
            else:
                y = int(self.y_inicial/self.espacio) + valores_y[i]

            # X coordinate
            height, width, channels = self.img_original.shape
            x = self.diente['coordenadas'].get(y,[0,width / 2,width])[i]

            # x-1 porque las curvas estaban quedando muy corridas
            puntos += [[x - 1, y * self.espacio]]

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

    def formato_dato(self, dato):
        '''Define el formato para los datos y el color de la línea'''

        opt = '_' if self.area == '_b' else ''

        if dato == 'margen':
            dato = opt + 'MARGEN'
            color_linea = 'rojo'
        elif dato == 'ni':
            dato = opt + 'N.I.'
            color_linea = None
        elif dato == 'lmg' and self.diente['superior'] and self.area == '_b':
            # Los dientes superiores no tienen _L.M.G
            return None, None
        elif dato == 'lmg':
            dato = opt + 'L.M.G'
            color_linea = 'verde'
        else:
            dato = opt + 'SONDAJE'
            color_linea = 'negro'

        return color_linea, dato

    def obtener_curvas(self, dato):
        '''Obtiene las coordenadas de las curvas'''

        opt = '_' if self.area == '_b' else ''
        color_linea, dato = self.formato_dato(dato)

        # Obtiene los puntos de la linea
        valores = self.diente['valores'].get(dato)
        if valores is None:
            return None, None
        valores = [int(y) for y in valores.split()]
        if dato == opt + 'SONDAJE':
            # La base de sondaje es la línea de Margen
            offset = [int(y) for y in self.diente['valores'][opt + 'MARGEN'].split()]
            valores = [valores[x] + offset[x] for x in range(3)]

        # Obtiene las coordenadas de la línea
        return color_linea, self.obtener_coordenadas(valores)

    def obtener_bordes(self, lado, margen, sondaje):
        '''Obtiene las coordenadas de los lados del diente entre margen y sondaje para pintar bolsas'''
        res = []
        indice = 0 if lado == 'izq' else 2
        indice_b = 0 if lado == 'der' else 2

        # a es el punto inicial y b es el punto final
        a, b = margen[indice], margen[indice_b] + sondaje[indice_b]

        # define el rango, si es el lado izquierdo, la reversa
        lista_y = range(a,b)
        if lado == 'izq':
            lista_y = reversed(lista_y)

        for y in lista_y:
            coord = self.obtener_coordenadas([y]*3)
            res.append(coord[indice])

        if len(res) == 0:
            return np.array(res, np.int32).reshape(0,2)

        return np.array(res, np.int32)

    def dibujar_curvas(self, dato):
        '''Dibuja las curvas de sondaje, margen y LMG'''
        color_linea, curva = self.obtener_curvas(dato)
        if curva is not None:
            cv2.polylines(
                self.img_procesada, self.recta_to_curva(curva),
                isClosed = False, color = color[color_linea],
                thickness = 2, lineType = cv2.LINE_AA)

    def pintar_bolsas(self):
        # Obtiene los valores
        opt = '_' if self.area == '_b' else ''
        margen = self.diente['valores'].get(self.formato_dato('margen')[1])
        sondaje = self.diente['valores'].get(self.formato_dato('sondaje')[1])
        ni = self.diente['valores'].get(self.formato_dato('ni')[1])

        if ni is not None:
            margen = [int(y) for y in margen.split()]
            sondaje = [int(y) for y in sondaje.split()]

            # Obtiene los puntos de las curvas
            _, curva_margen = self.obtener_curvas('margen')
            _, curva_sondaje = self.obtener_curvas('sondaje')
            curva_margen = self.recta_to_curva(curva_margen)
            curva_sondaje = self.recta_to_curva(curva_sondaje)

            # Divide las curvas en 3 segmentos
            curvas_m = np.array_split(curva_margen[0], 3)
            curvas_s = np.array_split(curva_sondaje[0], 3)

            # Define si debe pintar cada uno de los segmentos
            for i in range(3):
                # La bolsa es margen - sondaje, que es equivalente al negativo de ni
                if -ni[i] >= 4:
                    # Obtiene los puntos del polígono
                    puntos_m = curvas_m[i]
                    puntos_s = np.array(np.flip(curvas_s[i], axis=0), np.int32)
                    puntos_der = self.obtener_bordes('der', margen, sondaje)
                    puntos_izq = self.obtener_bordes('izq', margen, sondaje)
                    # Bolsa vs pseudobolsa
                    relleno = 'rojo' if margen[i] < 0 else 'negro'
                    # Agrega los puntos necesarios
                    if i == 0:
                        # tiene en cuenta los bordes izquierdos
                        puntos = np.concatenate((puntos_m, puntos_s, puntos_izq), axis=0)
                    elif i == 2:
                        # tiene en cuenta los bordes derechos
                        puntos = np.concatenate((puntos_m, puntos_der, puntos_s), axis=0)
                    else:
                        # es el del centro, no tiene en cuenta los bordes
                        puntos = np.concatenate((puntos_m, puntos_s), axis=0)
                    # Rellena el poligono
                    cv2.fillPoly(self.img_procesada, pts = [puntos], color = color[relleno])

    def __init__(self, diente, src, area, espacio):
        '''Inicializa un objeto NuevoDiente con la imagen original y la imagen sin alpha'''
        self.area = area
        self.diente = diente
        self.espacio = espacio
        # Define las coordenadas de las cuadrículas
        self.top, self.diente['coordenadas'] = coord(diente['diente'], area)
        # Carga las imágenes
        self.img_original = cv2.imread(src)
        self.img_procesada = read_transparent(src)
        self.img_procesada = self.pintar_ausente(self.img_procesada)
        self.img_procesada = self.bordes(self.img_procesada)
        # Si el diente está ausente, lo pinta de negro
        # Define los límites verticales
        self.y_inicial, self.y_final = self.limite_vertical()
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
            nuevo_diente.pintar_bolsas()
            # Dibuja las líneas correspondientes
            nuevo_diente.dibujar_curvas('sondaje')
            nuevo_diente.dibujar_curvas('margen')
            nuevo_diente.dibujar_curvas('lmg')
            # Agrega la imagen del diente al canvas
            canvas[canv_area + s] = stack_diente(canvas.get(canv_area + s), nuevo_diente)

    return canvas
