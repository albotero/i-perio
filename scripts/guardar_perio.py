from diente import Diente
from log import Log
import json
import os
import time

def file_path(archivo):
    '''Define la ruta donde se guardan los archivos para cada usuario'''
    # Más adelante buscará los datos de la sesión para cambiar la carpeta
    # del nombre de usuario
    return '/tmp/iperio/usuario1/' + archivo + '.perio'

class Guardar():

    def file_to_perio(archivo, silent = False):
        '''Carga un archivo .perio a un perio (diccionario de Dientes)'''
        ruta = file_path(archivo)
        if not silent:
            print('Cargando archivo: {}'.format(ruta))
        try:
            with open(ruta, 'r') as file:
                perio = json.load(file)
            for diente in perio.keys():
                perio[diente] = Diente(cargar = perio[diente])
            Log.out('Se cargó el archivo', 'success', silent)
            return perio
        except Exception as ex:
            Log.out(repr(ex), 'error', silent)

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
            Log.out('Se guardó el archivo', 'success', silent)
        except Exception as ex:
            Log.out(repr(ex), 'error', silent)
            return ex
