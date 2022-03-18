from grafico import nuevo_canvas
from main import nuevo_perio
import cv2
import random as rd
import unittest

class TestGrafico(unittest.TestCase):

    def test_grafico(self):
        # Crea nuevo perio
        perio = nuevo_perio()

        for num, diente in perio.items():
            if type(num) == int and num % 2 != 0:
                # Pone los dientes impares ausentes
                diente['atributos'] = 'Ausente'
            else:
                # En múltiplos de 4, genera margenes aleatorios
                if type(num) == int and num % 4 == 0:
                    diente['valores']['MARGEN'] = '{} {} {}'.format(
                        rd.randint(0, 10), rd.randint(0, 10), rd.randint(0, 10))
                    diente['valores']['_MARGEN'] = '{} {} {}'.format(
                        rd.randint(0, 10), rd.randint(0, 10), rd.randint(0, 10))

        # Obtiene las 4 imágenes del perio
        canvas = nuevo_canvas(perio)

        # Muestra las imagenes generadas
        for area, imagen in canvas.items():
            cv2.imshow(area, imagen)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Se asegura que si haya generado las imágenes
        self.assertTrue(canvas, 'Dict canvas vacío')

if __name__ == '__main__':
    unittest.main()
