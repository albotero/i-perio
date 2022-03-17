from grafico import nuevo_canvas
from main import nuevo_perio
import cv2
import unittest

class TestGrafico(unittest.TestCase):

    def test_grafico(self):
        perio = nuevo_perio()
        perio[34]['atributos'] = 'Ausente'
        perio[25]['atributos'] = 'Ausente'
        perio[12]['atributos'] = 'Ausente'
        perio[41]['atributos'] = 'Ausente'

        canvas = nuevo_canvas(perio)

        for area, imagen in canvas.items():
            cv2.imshow(area, imagen)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        self.assertTrue(canvas, 'Dict canvas vacío')

if __name__ == '__main__':
    unittest.main()
