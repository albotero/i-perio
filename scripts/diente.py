from itertools import cycle
import re

_opt_datos= {
    'VITALIDAD': ['-', '+'],
    'IMPLANTE': ['No', 'Si'],
    'MOVILIDAD': ['-', '1', '2', '3'],
    'FURCA': ['-', 'I', 'II', 'III'],
    'PLACA': ['0', '1']
    }

def get_titulos(diente):
    '''Devuelve el tuple correspondiente si es Superior o Inferior'''
    if diente['superior']:
        return ('IMPLANTE', 'VITALIDAD', 'FURCA', 'MOVILIDAD', 'PLACA', 'SUPURACIÓN',
            'SANGRADO', 'L.M.G', 'N.I.', 'SONDAJE', 'MARGEN', 'VESTIBULAR', '_PALATINO', '_MARGEN',
            '_SONDAJE', '_N.I.', '_SUPURACIÓN', '_SANGRADO', '_PLACA')
    else:
        return ('IMPLANTE', 'VITALIDAD', 'FURCA', 'MOVILIDAD', 'PLACA', 'SUPURACIÓN',
            'SANGRADO', 'L.M.G', 'N.I.', 'SONDAJE', 'MARGEN', 'LINGUAL', '_VESTIBULAR', '_MARGEN',
            '_SONDAJE', '_N.I.', '_L.M.G', '_SUPURACIÓN', '_SANGRADO', '_PLACA')

def next_dato(titulo, valor_actual):
    lista_opt = _opt_datos[titulo]
    if valor_actual not in lista_opt:
        indice_actual = -1
    else:
        indice_actual = lista_opt.index(valor_actual)
        if lista_opt[indice_actual] is lista_opt[-1]:
            indice_actual = -1
    return lista_opt[indice_actual + 1]

def init_valores(diente, titulos):
    '''Crea un diccionario con los datos del diente correspondiente'''
    res = {}
    for val in titulos:
        res[val] = None
        if 'SANGRADO' in val or 'SUPURACIÓN' in val:
            res[val] = False, False, False
        elif val in _opt_datos.keys():
            res[val] = _opt_datos[val][0]
    return res

class Diente(dict):
    '''Define el objeto para cada diente'''

    _atributos = ('Normal', 'Ausente', 'Extruido', 'Intruido')

    def calcular_ni(self):
        '''Si se han especificado margen y sondaje, calcula el nivel de inserción
            Si se especifica opt = '_' usa los datos de _MARGEN y _SONDAJE en _N.I.'''
        for opt in ['', '_']:
            # Si no ha especificado Margen y Sondaje deja vacío el Nivel de inserción
            if self['valores'][opt+'MARGEN'] is None or self['valores'][opt+'SONDAJE'] is None:
                self['valores'][opt+'N.I.'] = None
            else:
                res = []
                margen = self['valores'][opt+'MARGEN']
                sondaje = self['valores'][opt+'SONDAJE']
                for i in range(3):
                    res.append(margen[i] - sondaje[i])
                self['valores'][opt+'N.I.'] = res

    def __init__(self, diente = None, cargar = None):
        '''Inicializa o carga el diente'''
        if diente:
            self['diente'] = diente
            self['superior'] = diente <= 28 or \
                              (diente >= 51 and diente <= 68)
            self['atributos'] = self._atributos[0]
            self['valores'] = init_valores(diente, get_titulos(self))
        if cargar:
            self['diente'] = cargar['diente']
            self['superior'] = cargar['superior']
            self['atributos'] = cargar['atributos']
            self['valores'] = cargar['valores']
        self.calcular_ni()
