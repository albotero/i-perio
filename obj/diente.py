import re

class Diente:
    '''Define el objeto para cada diente'''

    _atributos = ('Normal', 'Ausente', 'Extruido', 'Intruido')

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
            #Inicializa cada valor en el diccionario según si usa 3 números, 1 número o guión
            if re.search(r'L\.M\.G|SONDAJE|MARGEN|SUPURA|SANGRA', val):
                res[val] = (0,0,0)
            elif re.search(r'N\.I', val):
                res[val] = 0
            else:
                res[val] = '-'
        return res

    def __init__(self, diente):
        '''Inicializa el diente'''
        self.diente = diente
        self.atributos = Diente._atributos[0]
        self.titulos = Diente.get_titulos(diente)
        self.valores = Diente.init_valores(diente, self.titulos)

        # Muestra el diccionario inicializado, para efectos de prueba, esto se quita después
        print(self.valores)

# Inicializar objetos... Esto se debe hacer desde la función externa cuando esté implementado
diente_11 = Diente(11)
diente_11 = Diente(34)
