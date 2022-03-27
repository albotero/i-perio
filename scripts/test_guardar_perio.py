from .diente import Diente
from .guardar_perio import Guardar
from .main import *
import os
import unittest

class TestGuardarPerio(unittest.TestCase):

    tmp_file = 'test_perio_to_file'

    def test_perio_to_file(self):
        '''Si devuelve un valor tuvo un error'''
        res = Guardar.perio_to_file(nuevo_perio(), self.tmp_file, silent = True)
        self.assertIsNone(res, "Error al guardar archivo: {}".format(res))

    def test_file_to_perio(self):
        '''Revisa que obtenga instancias de Diente al leer el archivo'''
        Guardar.perio_to_file(nuevo_perio(), self.tmp_file, silent = True)
        perio = Guardar.file_to_perio(self.tmp_file, silent = True)
        for diente in perio:
            if diente.isnumeric():
                self.assertIsInstance(perio[diente], Diente)
                break

if __name__ == '__main__':
    unittest.main()
