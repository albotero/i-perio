import re

def get_titulos(diente):
    '''Devuelve el tuple correspondiente si es Superior o Inferior'''
    superior = diente <= 28 or (diente >= 51 and diente <= 68)
    if superior:
        return ('IMPLANTE', 'VITALIDAD', 'FURCA', 'MOVILIDAD', 'PLACA', 'SUPURACIÓN',
            'SANGRADO', 'L.M.G', 'N.I.', 'SONDAJE', 'MARGEN', 'VESTIBULAR', '_PALATINO', '_MARGEN',
            '_SONDAJE', '_N.I.', '_SUPURACIÓN', '_SANGRADO', '_PLACA')
    else:
        return ('IMPLANTE', 'VITALIDAD', 'FURCA', 'MOVILIDAD', 'PLACA', 'SUPURACIÓN',
            'SANGRADO', 'L.M.G', 'N.I.', 'SONDAJE', 'MARGEN', 'LINGUAL', '_VESTIBULAR', '_MARGEN',
            '_SONDAJE', '_N.I.', '_L.M.G', '_SUPURACIÓN', '_SANGRADO', '_PLACA')

def init_valores(diente, titulos):
    '''Crea un diccionario con los datos del diente correspondiente'''
    res = {}
    for val in titulos:
        res[val] = None
    return res

class Diente(dict):
    '''Define el objeto para cada diente'''

    _atributos = ('Normal', 'Ausente', 'Extruido', 'Intruido')

    def calcular_ni(self, opt = ''):
        '''Si se han especificado margen y sondaje, calcula el nivel de inserción
            Si se especifica opt = '_' usa los datos de _MARGEN y _SONDAJE en _N.I.'''

        # Si no ha especificado Margen y Sondaje deja vacío el Nivel de inserción
        if self['valores'][opt+'MARGEN'] is None or self['valores'][opt+'SONDAJE'] is None:
            self['valores'][opt+'N.I.'] = None
        else:
            res = []
            for i in range(3):
                res.append(self['valores'][opt+'MARGEN'][i] - self['valores'][opt+'SONDAJE'][i])
            self['valores'][opt+'N.I.'] = tuple(res)

    def __init__(self, diente = None, cargar = None):
        '''Inicializa o carga el diente'''
        if diente:
            self['diente'] = diente
            self['atributos'] = Diente._atributos[0]
            self['valores'] = init_valores(diente, get_titulos(diente))
        if cargar:
            self['diente'] = cargar['diente']
            self['atributos'] = cargar['atributos']
            self['valores'] = cargar['valores']
