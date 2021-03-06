#!/usr/bin/env python3

from .diente import Diente
from .diente_csv import coord, coord_furca
from .process_images import *

import cv2
import numpy as np
import os
import re

class NuevoDiente(object):
    height = 160

    def get(self):
        '''Devuelve la imagen procesada'''
        return self.img_procesada

    def bordes(self):
        '''Alinea el diente con la cuadrícula añadiendo un espacio en la parte superior
        y añade un borde en la parte inferior para que la imagen sea de 140px'''
        y, x, _ = self.img_procesada.shape
        self.bottom = self.height - (self.top + y)

        self.img_procesada = cv2.copyMakeBorder(self.img_procesada,
                self.top, self.bottom, 0, 0, cv2.BORDER_CONSTANT,
                value=color['blanco'])

    def pintar_ausente(self):
        '''Pinta de negro si el diente tiene el atributo Ausente'''
        if self.diente['atributos'] == 'Ausente':
            self.img_procesada = process_fill(self.img_original, self.img_procesada)

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
                linea_0 = int(self.y_final/self.espacio)
                y = linea_0 - valores_y[i]
            else:
                linea_0 = int(self.y_inicial/self.espacio)
                y = linea_0 + valores_y[i]

            # X coordinate
            height, width, channels = self.img_original.shape
            x = self.diente['coordenadas'].get(y,[0,width / 2,width])[i]

            # offset porque las curvas estaban quedando muy corridas
            offset_x = -1
            offset_y = -1 if self.diente['superior'] and self.area == '_b' else 1
            puntos += [[
                (x + offset_x) * self.zoom_factor,
                (y * self.espacio + offset_y) * self.zoom_factor
                ]]

        return np.array(puntos, np.int32)

    def formato_dato(self, dato):
        '''Define el formato para los datos y el color de la línea'''

        opt = '_' if self.area == '_b' else ''

        if dato == 'margen':
            dato = opt + 'MARGEN'
            color_linea = 'rojo'
        elif dato == 'ni':
            dato = opt + 'NI'
            color_linea = None
        elif dato == 'lmg':
            # Los dientes superiores no tienen _LMG
            if self.diente['superior'] and self.area == '_b':
                return None, None
            dato = opt + 'LMG'
            color_linea = 'verde'
        else:
            dato = opt + 'SONDAJE'
            color_linea = 'negro'

        return color_linea, dato

    def obtener_puntos(self, dato):
        '''Obtiene las coordenadas de las curvas'''

        opt = '_' if self.area == '_b' else ''
        color_linea, dato = self.formato_dato(dato)

        # Obtiene los puntos de la linea
        valores = self.diente['valores'].get(dato)
        margen = self.diente['valores'][opt + 'MARGEN']

        if (not Diente.margen_sondaje_valido(valores) or
            not Diente.margen_sondaje_valido(margen)):
            return None, None

        valores = Diente.format_margen_sondaje(valores)
        margen = Diente.format_margen_sondaje(margen)

        # Los margenes son negativos (+ hacia la corona y - hacia la raíz)
        if dato == opt + 'MARGEN':
            valores = [-x for x in valores]
        if dato == opt + 'SONDAJE':
            # La base de sondaje es la línea de Margen
            valores = [valores[x] - margen[x] for x in range(3)]

        # Obtiene las coordenadas de la línea
        res_valores = np.array(self.obtener_coordenadas(valores))
        return color_linea, res_valores

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

    def dibujar_margen_sondaje(self, dato):
        '''Dibuja las curvas de sondaje y margen'''
        color_linea, curva = self.obtener_puntos(dato)
        self.img_procesada = dibujar_curva(self.img_procesada, color_linea, curva)

    def pintar_bolsas(self):
        # Obtiene los valores
        opt = '_' if self.area == '_b' else ''
        margen = self.diente['valores'].get(self.formato_dato('margen')[1])
        sondaje = self.diente['valores'].get(self.formato_dato('sondaje')[1])

        if (Diente.margen_sondaje_valido(margen) and
            Diente.margen_sondaje_valido(sondaje)):
            # Obtiene lista de datos
            margen = Diente.format_margen_sondaje(margen)
            sondaje = Diente.format_margen_sondaje(sondaje)
            sangrado = self.diente['valores'][opt + 'SANGRADO']

            # Lo vuelve negativo ya que (+) es coronal y (-) es radical
            margen = [-y for y in margen]

            # Obtiene los puntos de las curvas
            _, curva_margen = self.obtener_puntos('margen')
            _, curva_sondaje = self.obtener_puntos('sondaje')
            curva_margen = recta_to_curva(curva_margen.tolist())
            curva_sondaje = recta_to_curva(curva_sondaje.tolist())

            # Divide las curvas en 3 segmentos
            curvas_m = np.array_split(curva_margen[0], 3)
            curvas_s = np.array_split(curva_sondaje[0], 3)

            # Define si hay una bolsa o pseudobolsa para pintar
            for i in range(3):

                if sondaje[i] >= 4 and sangrado[i]:
                    # Ambas tienen sondaje aumentado y encía inflamada (sangrado)
                    # -> Bolsa verdadera (negra): Pérdida de inserción
                    # -> Pseudobolsa (roja): Sin pérdida de inserción
                    perdida_insercion = -margen[i] - sondaje[i] < 0
                    relleno = 'negro' if perdida_insercion else 'rojo'
                else:
                    # No tiene bolsa
                    continue

                # Obtiene los puntos del polígono
                puntos_m = curvas_m[i]
                puntos_s = np.array(np.flip(curvas_s[i], axis=0), np.int32)
                puntos_der = self.obtener_bordes('der', margen, sondaje)
                puntos_izq = self.obtener_bordes('izq', margen, sondaje)

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

    def obtener_coord_lmg(self, canvas_previo):
        '''Obtiene las coordenadas de lmg en la imagen entera'''
        # Obtiene la coordenada x de la imagen en el canvas
        if canvas_previo is None:
            x_diente = 0
        else:
            _, x_diente, _ = canvas_previo.shape

        # Obtiene en valor de la LMG de el diente actual
        lmg = self.diente['valores'].get(self.formato_dato('lmg')[1])
        margen = self.diente['valores'].get(self.formato_dato('margen')[1])

        # Si no está definido, pone un valor por defecto
        if self.diente['atributos'] == 'Ausente' or lmg is None or not lmg.isnumeric() or margen is None:
            lmg = 20
            margen = '0 0 0'

        # LMG con base en el margen
        lmg = int(lmg) - int(margen.split(' ')[1])

        # Obtiene las coordenadas del punto en la imagen actual
        coord = self.obtener_coordenadas([lmg]*3)[1]
        # Obtiene la coordenada x en el canvas
        coord[0] += x_diente

        return coord

    def dibujar_in_extruido(self):
        # Define las coordenadas de los puntos
        height, width, _ = self.img_procesada.shape
        x = int(width / 2)
        y1 = int(6 * self.zoom_factor)
        y2 = y1 + int(10 * self.zoom_factor)

        if self.diente['superior']:
            y1 = height - y1
            y2 = height - y2

        # Asigna las coordenadas según correspondan
        if 'Intruido' in self.diente['atributos']:
            coord_a, coord_b = (x, y1), (x, y2)
        elif 'Extruido' in self.diente['atributos']:
            coord_a, coord_b = (x, y2), (x, y1)
        else:
            return

        color_flecha = 'rojo'
        self.img_procesada = dibujar_flecha(self.img_procesada, coord_a, coord_b, color_flecha)

    def dibujar_furcas(self):
        '''Pinta un círculo en las furcas si tiene un valor válido'''

        if self.diente['superior']:
            # Molares superiores
            if self.diente['diente'] % 10 >= 6:
                furcas = [ 'V' ] if self.area == '_a' else [ 'MP', 'DP' ]
            # Premolares superiores
            elif self.diente['diente'] % 10 == 4:
                furcas = [ 'D' ] if self.area == '_a' else [ 'M' ]
            # Es un diente sin furcas, no hace nada
            else:
                return
        else:
            # Molares inferiores
            if self.diente['diente'] % 10 >= 6:
                furcas = [ 'L' ] if self.area == '_a' else [ 'V' ]
            # Es un diente sin furcas, no hace nada
            else:
                return

        for f in furcas:
            # Evalúa si se especificaron furcas válidas
            patron_valor = r'{}I+'.format(f)
            if self.diente['valores']['FURCA'] is None or \
                re.search(patron_valor, self.diente['valores']['FURCA']) is None:
                continue

            # Obtiene las coordenadas de la furca
            patron_coord = r'\[{}:(\d+)\*(\d+)\]'.format(f)
            x, y = coord_furca(self.diente['diente'], patron_coord)
            x = int(int(x) * self.zoom_factor)
            y = int(int(y) * self.zoom_factor)

            self.img_procesada = cv2.circle(self.img_procesada,
                                            (x, y),
                                            radius = int(5 * self.zoom_factor),
                                            color = color['negro'],
                                            thickness = -1) # thickness -1 fills the circle
            self.img_procesada = cv2.circle(self.img_procesada,
                                            (x, y),
                                            radius = int(5 * self.zoom_factor),
                                            color = color['blanco'],
                                            thickness = 1)


    def __init__(self, diente, src, area, espacio, zoom_factor = 1):
        '''Inicializa un objeto NuevoDiente con la imagen original y la imagen sin alpha'''
        self.area = area
        self.diente = diente
        self.espacio = espacio
        # Define las coordenadas de las cuadrículas
        limite_i, limite_f = self.limite_vertical()
        linea_0 = limite_f if diente['superior'] else limite_i
        linea_0 = int(linea_0 / self.espacio)
        self.top, self.diente['coordenadas'] = coord(diente['diente'], area,
                diente['superior'], diente['valores']['IMPLANTE'] == 'Si', linea_0)
        # Define si la imagen es normal o implante
        if self.diente['valores']['IMPLANTE'] == 'Si' and self.diente['atributos'] != 'Ausente':
            src = src.replace('dientes', 'implantes')
        # Carga las imágenes
        self.img_original = cv2.imread(src)
        self.img_procesada = read_transparent(src)
        self.pintar_ausente()
        self.bordes()
        # Define los límites verticales
        self.y_inicial, self.y_final = self.limite_vertical()
        # Dibuja las cuadrículas
        self.dibujar_cuadriculas()
        # Amplifica la imagen para poder dibujar las líneas delgadas
        self.zoom_factor = zoom_factor
        self.img_procesada = zoom(self.img_procesada, zoom_factor)


def stack_diente(canvas, diente):
    '''Apila horizontalmente el diente nuevo en el canvas actual'''
    # Obtiene la imagen procesada
    nuevo_diente = diente.get()
    # Si es la primer imagen del canvas, devuelve el canvas
    if canvas is None:
        return nuevo_diente
    # Devuelve la imagen resultante
    return np.concatenate((canvas, nuevo_diente), axis = 1)

def agregar_lmg(nuevo_diente, canvas_previo):
    '''Agrega la LMG del nuevo diente a las lmg previas'''
    lmg = canvas_previo[1]
    nueva_lmg = [nuevo_diente.obtener_coord_lmg(canvas_previo[0])]

    # Si es el primer valor de la LMG pone la misma y pero en x = 0
    if (lmg[0] == np.array([0,0])).all():
        y = nueva_lmg[0][1]
        lmg = [np.array([0, y], np.int32)]

    return np.concatenate((lmg, nueva_lmg), axis=0)

def nuevo_canvas(perio, filtro=None):
    '''Crea los 4 canvas con las imágenes de los dientes'''
    canvas = {}
    dimensiones = {}
    espacio = 7
    zoom_factor = 1.5

    for num, diente in perio.items():
        # Si no es un diente no hace nada
        if type(diente) is not Diente:
            continue

        canv_area = 'sup' if diente['superior'] else 'inf'

        if perio['pediatrico']:
            num -= 40

        for s in ['_a', '_b']:
            # Si hay filtro, lo aplica
            if filtro is not None and (canv_area + s) not in filtro:
                continue

            src = 'img/dientes/{}{}.png'.format(num, s)
            # Carga la imagen del diente
            nuevo_diente = NuevoDiente(diente, src, s, espacio, zoom_factor)
            if diente['atributos'] != 'Ausente':
                # Pinta las bolsas y pseudobolsas
                nuevo_diente.pintar_bolsas()
                # Dibuja las líneas correspondientes
                nuevo_diente.dibujar_margen_sondaje('sondaje')
                nuevo_diente.dibujar_margen_sondaje('margen')
                # Dibuja las furcas
                nuevo_diente.dibujar_furcas()
                # Dibuja flecha si lo requiere
                nuevo_diente.dibujar_in_extruido()

            # Obtiene el canvas previo
            canvas_previo = canvas.get(
                    canv_area + s,
                    [None, np.array([[0,0]], np.int32), np.array([[0,0]], np.int32)]
                    )
            # Agrega la imagen del diente al canvas
            canvas[canv_area + s] = [
                stack_diente(canvas_previo[0], nuevo_diente),
                agregar_lmg(nuevo_diente, canvas_previo)
                ]
            # Agrega las dimensiones del diente
            dimensiones[canv_area + s] = dimensiones.get(canv_area + s, [0]) + [nuevo_diente.img_procesada.shape[1]]

    # Dibuja la LMG
    for key, cvs in canvas.items():
        # Los dientes superiores no tienen _LMG
        if key != 'sup_b':
            # Crea una curva por cada grupo de LMG contiguos que tienen un valor válido
            nuevas_lmg = []

            img, lmg = cvs

            # Evalúa si los puntos contiguos tienen un valor válido
            for i, punto in enumerate(lmg):
                x, y = punto
                _, y_prev = lmg[i-1]
                x_diente = sum(dimensiones[key][:i])
                w_diente = dimensiones[key][i]

                # Bordes izquierdos
                nuevo_punto = [[x - 15, y]]
                if i == 0 or y_prev <= 0 or y_prev >= 200:
                    # Inicializa una nueva curva
                    nuevo_punto = [[x_diente, y]]
                    nuevas_lmg.append( nuevo_punto )
                elif y <= 0 or y >= 200:
                    continue

                nuevas_lmg[-1] = np.append(nuevas_lmg[-1], nuevo_punto, axis=0)

                # Bordes derechos
                borde_der = x + 15
                if i == len(lmg) - 1 or lmg[i+1][1] <= 0 or lmg[i+1][1] >= 200:
                    borde_der = x_diente + w_diente
                nuevo_punto = [np.array([borde_der, y], np.int32)]
                nuevas_lmg[-1] = np.append(nuevas_lmg[-1], nuevo_punto, axis=0)

            # Dibuja las curvas de LMG
            for curva in nuevas_lmg:
                cvs[0] = dibujar_curva(cvs[0], 'verde', curva, tension = .35)

        # Borra los datos de la LMG del diccionario para devolver solo la imagen
        canvas[key] = zoom(cvs[0], 1/1.35)

    return canvas
