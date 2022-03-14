from diente import Diente
from guardar_perio import Guardar
from main import *
import os
import unittest

class TestGuardarPerio(unittest.TestCase):

    def test_perio_to_file(self):
        '''Si devuelve un valor tuvo un error'''
        res = Guardar.perio_to_file(nuevo_perio(), 'test_perio_to_file', silent = True)
        self.assertIsNone(res, "Error al guardar archivo: {}".format(res))

    def test_file_to_perio(self):
        perio = Guardar.file_to_perio('test_perio_to_file', silent = True)
        for diente in perio:
            self.assertIsInstance(perio[diente], Diente)
            break

if __name__ == '__main__':
    unittest.main()
