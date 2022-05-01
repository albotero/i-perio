from .diente import Diente
from .log import Log
import json
import os

from datetime import datetime
import pytz

formato_dt = '%Y-%m-%d, %H:%M:%S'

def file_path(id_usuario, archivo = None):
    '''Define la ruta donde se guardan los archivos para cada usuario'''
    if archivo:
        return f'../periodontogramas/{id_usuario}/{archivo}.perio'
    else:
        return f'../periodontogramas/{id_usuario}/'

class Guardar():

    def file_to_perio(archivo, id_usuario = 'invitado', silent = False, throwerror = False):
        '''Carga un archivo .perio a un perio (diccionario de Dientes)'''
        ruta = file_path(id_usuario, archivo)
        if not silent:
            print('Cargando archivo: {}'.format(ruta))
        try:
            with open(ruta, 'r') as file:
                perio = json.load(file)
            for diente in perio.keys():
                if diente.isnumeric():
                    perio[diente] = Diente(cargar = perio[diente])
            Log.out('Se cargó el archivo', 'success', silent)
            return perio
        except Exception as ex:
            Log.out(ex, 'error', silent,
                    origen='guardar_perio.file_to_perio')
            if throwerror:
                raise Exception(ex)

    def perio_to_file(perio, archivo, id_usuario, silent = False):
        '''Guarda el perio (diccionario de Dientes) a un archivo .perio'''
        ruta = file_path(id_usuario, archivo)

        # Actualiza la fecha de modificación
        tz = pytz.timezone('America/Bogota')
        hora = datetime.now(tz).strftime(formato_dt)
        perio['modificado'] = hora

        if not silent:
            print('Guardando archivo: {}'.format(ruta))
        try:
            os.makedirs(os.path.dirname(ruta), exist_ok = True)
            with open(ruta, 'w') as file:
                file.write(json.dumps(perio, indent=3))
            Log.out('Se guardó el archivo', 'success', silent)
        except Exception as ex:
            Log.out(ex, 'error', silent,
                    origen='guardar_perio.perio_to_file')
            return ex

    def list_perios(id_usuario, orden, desc):
        ''' Evalúa la carpeta del usuario y devuelve un diccionario con:
            nombre de archivo, creación y modificación '''
        ruta = file_path(id_usuario)
        lista = {}
        try:
            os.makedirs(ruta, exist_ok=True)
            filenames = os.listdir(ruta)

            for filename in filenames:
                with open(os.path.join(ruta, filename), 'r') as file:
                    perio = json.load(file)
                valores = {
                    'filename': filename.replace('.perio', ''),
                    'creacion': datetime.strptime(perio['creado'], formato_dt),
                    'modificacion': datetime.strptime(perio['modificado'], formato_dt),
                    'paciente_id': perio['paciente']['id'],
                    'paciente_nombre': perio['paciente']['nombre']
                }
                lista[valores[orden]] = valores
        except Exception as ex:
            Log.out(ex, 'error', silent=False,
                    origen='guardar_perio.list_perios')
            return ex

        lista = dict(sorted(lista.items(), reverse=desc))

        return lista.values()

    def eliminar_perio(id_usuario, id_perio):
        '''Elimina el archivo del periodontograma guardado'''
        ruta = file_path(id_usuario, id_perio)
        try:
            os.remove(ruta)
        except Exception as ex:
            Log.out(ex, 'error', silent=False,
                    origen='guardar_perio.eliminar_perio')
            return ex
