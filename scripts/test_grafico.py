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
            if type(num) is not int:
                continue

            # Todos los dientes con mismo margen y sondaje
            margen = '0 0 0'
            sondaje = '1 1 1'
            diente['valores']['MARGEN'] = margen
            diente['valores']['_MARGEN'] = margen
            diente['valores']['SONDAJE'] = sondaje
            diente['valores']['_SONDAJE'] = sondaje
            continue

            if type(num) == int and num % 2 != 0:
                # Pone los dientes impares ausentes
                diente['atributos'] = 'Ausente'
            else:
                # En múltiplos de 4, genera margenes aleatorios
                if type(num) == int and num % 4 == 0:
                    diente['valores']['MARGEN'] = '{} {} {}'.format(
                        rd.randint(-3, 8), rd.randint(-3, 8), rd.randint(-3, 8))
                    diente['valores']['_MARGEN'] = '{} {} {}'.format(
                        rd.randint(-3, 8), rd.randint(-3, 8), rd.randint(-3, 8))
                    diente['valores']['SONDAJE'] = '{} {} {}'.format(
                        rd.randint(0, 7), rd.randint(0, 7), rd.randint(0, 7))
                    diente['valores']['_SONDAJE'] = '{} {} {}'.format(
                        rd.randint(0, 7), rd.randint(0, 7), rd.randint(0, 7))
                elif type(num) == int:
                    diente['valores']['MARGEN'] = '1 0 1'
                    diente['valores']['_MARGEN'] = '0 0 0'
                    diente['valores']['SONDAJE'] = '1 1 1'
                    diente['valores']['_SONDAJE'] = '3 2 4'

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
