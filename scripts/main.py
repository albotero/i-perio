#!/usr/bin/env python3

from .diente import Diente
from .grafico import nuevo_canvas
from .guardar_perio import Guardar

from datetime import datetime
import pytz

def crear_diente(indice, pediatrico):
    '''Crea un nuevo Diente, el número del diente lo toma según el índice'''
    cuadrante = indice // 8 + 1
    diente = indice % 8 + 1

    #Invierte los cuadrantes 3 y 4 para que primero sea 4 y luego 3
    if cuadrante == 3:
        cuadrante = 4
    elif cuadrante == 4:
        cuadrante = 3

    #En los cuadrantes 1 y 4 el conteo se enumera de 8 a 1
    if cuadrante == 1 or cuadrante == 4:
        diente = 9 - diente

    #Obtiene el número del diente según el cuadrante
    numero_diente = cuadrante * 10 + diente

    if pediatrico:
        numero_diente += 40
        #La dentición decidua solo tiene hasta 5 dientes
        if diente > 5:
            return

    return Diente(diente = numero_diente)

def nuevo_perio(nombre, id, dob, pediatrico = False):
    '''Inicializa un nuevo periodontograma'''

    tz = pytz.timezone('America/Bogota')
    hora = datetime.now(tz).strftime('%Y-%m-%d, %H:%M:%S')

    perio = {
        'pediatrico': pediatrico,
        'creado': hora,
        'modificado': hora,
        'paciente': {
            'nombre': nombre,
            'id': id,
            'dob': dob
        }
    }
    for i in range(32):
        nuevo_diente = crear_diente(i, pediatrico)
        if nuevo_diente is not None:
            perio[nuevo_diente['diente']] = nuevo_diente
    return perio
