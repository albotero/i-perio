import re

class Diente:
    '''Define el objeto para cada diente'''

    _atributos = ('Normal', 'Ausente', 'Extruido', 'Intruido')

    diente = 0
    atributos = ''
    titulos = ()
    valores = {}

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

    def calcular_ni(self, opt = ''):
        '''Si se han especificado margen y sondaje, calcula el nivel de inserción
            Si se especifica opt = '_' usa los datos de _MARGEN y _SONDAJE en _N.I.'''

        # Si no ha especificado Margen #,#,# y Sondaje #,#,# deja vacío el Nivel de inserción
        if self.valores[opt+'MARGEN'] is None or self.valores[opt+'SONDAJE'] is None:
            self.valores[opt+'N.I.'] = None
            return
        res = []
        for i in range(3):
            res.append(self.valores[opt+'MARGEN'][i] - self.valores[opt+'SONDAJE'][i])
        self.valores[opt+'N.I.'] = tuple(res)

    def __init__(self, diente):
        '''Inicializa el diente'''
        self.diente = diente
        self.atributos = Diente._atributos[0]
        self.titulos = Diente.get_titulos(diente)
        self.valores = Diente.init_valores(diente, self.titulos)

# Inicializar objetos... Esto se debe hacer desde la función externa cuando esté implementado
diente_11 = Diente(11)
diente_11.valores['MARGEN'] = -2, -1, -3
diente_11.valores['SONDAJE'] = 4, 1, 0
diente_11.calcular_ni()
print(diente_11.valores)
print('------------------')
diente_34 = Diente(34)
diente_34.calcular_ni(opt = '_')
print(diente_34.valores)
print(diente_34.valores['N.I.'])
