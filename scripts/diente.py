_opt_datos= {
    'VITALIDAD': ['-', '+'],
    'IMPLANTE': ['No', 'Si'],
    'MOVILIDAD': ['-', '1', '2', '3'],
    'PLACA': ['0', '1']
    }

def get_titulos(diente):
    '''Devuelve el tuple correspondiente si es Superior o Inferior'''
    if diente['superior']:
        return ('IMPLANTE', 'VITALIDAD', 'FURCA', 'MOVILIDAD', 'PLACA', 'SUPURACIÓN',
            'SANGRADO', 'LMG', 'NI', 'SONDAJE', 'MARGEN', 'VESTIBULAR', '_PALATINO', '_MARGEN',
            '_SONDAJE', '_NI', '_SUPURACIÓN', '_SANGRADO', '_PLACA')
    else:
        return ('IMPLANTE', 'VITALIDAD', 'FURCA', 'MOVILIDAD', 'PLACA', 'SUPURACIÓN',
            'SANGRADO', 'LMG', 'NI', 'SONDAJE', 'MARGEN', 'LINGUAL', '_VESTIBULAR', '_MARGEN',
            '_SONDAJE', '_NI', '_LMG', '_SUPURACIÓN', '_SANGRADO', '_PLACA')

def init_valores(diente, titulos):
    '''Crea un diccionario con los datos del diente correspondiente'''
    res = {}
    for val in titulos:
        res[val] = None
        if 'SANGRADO' in val or 'SUPURACIÓN' in val:
            res[val] = False, False, False
        elif val.replace('_', '') in _opt_datos.keys():
            res[val] = _opt_datos[val.replace('_', '')][0]
    return res

class Diente(dict):
    '''Define el objeto para cada diente'''

    _atributos = ('Normal', 'Ausente', 'Extruido', 'Intruido')

    def margen_sondaje_valido(valor: str):
        try:
            lista = valor.strip().split(' ')
            lista = [int(y) for y in lista]
            return len(lista) == 3
        except:
            return False

    def format_margen_sondaje(valor: str):
        return [int(i) for i in valor.split()]

    def calcular_ni(self):
        '''Si se han especificado margen y sondaje, calcula el nivel de inserción
            Si se especifica opt = '_' usa los datos de _MARGEN y _SONDAJE en _NI'''
        for opt in ['', '_']:
            # Si no ha especificado Margen y Sondaje deja vacío el Nivel de inserción
            if (not Diente.margen_sondaje_valido(self['valores'][opt+'MARGEN']) or
                not Diente.margen_sondaje_valido(self['valores'][opt+'SONDAJE'])):
                self['valores'][opt+'NI'] = None
            else:
                res = []
                margen = Diente.format_margen_sondaje(self['valores'][opt+'MARGEN'])
                sondaje = Diente.format_margen_sondaje(self['valores'][opt+'SONDAJE'])
                for i in range(3):
                    res.append(margen[i] - sondaje[i])
                self['valores'][opt+'NI'] = res

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
