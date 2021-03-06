from .diente import Diente
from .grafico import nuevo_canvas
from .main import nuevo_perio
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

            '''# Todos los dientes con mismo margen y sondaje
            margen = '0 0 0'
            sondaje = '1 1 1'
            diente['valores']['MARGEN'] = margen
            diente['valores']['_MARGEN'] = margen
            diente['valores']['SONDAJE'] = sondaje
            diente['valores']['_SONDAJE'] = sondaje
            continue'''

            diente['atributos'] = Diente._atributos[num % 4]

            if num % 3 == 0:
                diente['valores']['IMPLANTE'] = True

            # Datos aleatorios
            for opt in ['', '_']:
                diente['valores'][opt + 'MARGEN'] = \
                    rd.randint(-3, 1), rd.randint(-3, 1), rd.randint(-3, 1)
                diente['valores'][opt + 'SONDAJE'] = \
                    rd.randint(0, 7), rd.randint(0, 7), rd.randint(0, 7)
                diente['valores'][opt +'SANGRADO'] = \
                    not rd.getrandbits(1), not rd.getrandbits(1), not rd.getrandbits(1)
                diente['valores'][opt +'SUPURACIÓN'] = \
                    not rd.getrandbits(1), not rd.getrandbits(1), not rd.getrandbits(1)

            # Algunos dientes no se les especifica LMG
            diente['valores']['LMG'] = str(rd.randint(6,10))
            # Genera las _LMG de los dientes inferiores
            if not diente['superior']:
                diente['valores']['_LMG'] = str(rd.randint(6,10))

            diente.calcular_ni()

        # Obtiene las 4 imágenes del perio
        canvas = nuevo_canvas(perio)

        # Muestra las imagenes generadas
        '''for area, imagen in canvas.items():
            cv2.imshow(area, imagen[0])
        cv2.waitKey(0)
        cv2.destroyAllWindows()'''

        # Se asegura que si haya generado las imágenes
        self.assertTrue(canvas, 'Dict canvas vacío')

        # Devuelve el canvas para mostrarlo en el ejemplo en index.html
        return canvas

if __name__ == '__main__':
    unittest.main()
