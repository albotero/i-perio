from diente import Diente
import json
import os
import time

def file_path(archivo):
    '''Define la ruta donde se guardan los archivos para cada usuario'''
    # Más adelante buscará los datos de la sesión para cambiar la carpeta
    # del nombre de usuario
    return '/tmp/iperio/usuario1/' + archivo + '.perio'

class Guardar():

    def file_to_perio(archivo):
        '''Carga un archivo .perio a un perio (diccionario de Dientes)'''
        pass

    def perio_to_file(perio, archivo = None, silent = False):
        '''Guarda el perio (diccionario de Dientes) a un archivo .perio'''
        if archivo is None:
            archivo = time.strftime("%Y%m%d-%H%M%S")
        ruta = file_path(archivo)
        if not silent:
            print('Guardando archivo: {}'.format(ruta))
        try:
            os.makedirs(os.path.dirname(ruta), exist_ok = True)
            with open(ruta, 'w') as file:
                file.write(json.dumps(perio, indent=3))
        except ex:
            return ex