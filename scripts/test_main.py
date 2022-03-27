from .main import *
import unittest

class TestPerio(unittest.TestCase):

    def test_perio_vacio(self):
        perio = nuevo_perio()
        self.assertEqual(
            len([d for d in perio if type(d) == int]), 32,
            'Perio contiene {} y no 32 dientes'.format(len(perio)))

    def test_perio_vacio_ped(self):
        perio = nuevo_perio(pediatrico = True)
        self.assertEqual(
            len([d for d in perio if type(d) == int]), 20,
            'Perio contiene {} y no 20 dientes'.format(len(perio)))

if __name__ == '__main__':
    unittest.main()
