from .colors import Colors
from datetime import datetime

log_file = '../i-perio.log'

type_list = {
    'success': {
        'title': 'OK: ',
        'style': ['bold', 'green']
        },
    'info': {
        'title': 'INFO: ',
        'style': ['bold', 'cyan']
        },
    'error': {
        'title': 'ERROR: ',
        'style': ['bold', 'red']
        }
    }

class Log:

    def out(msg, type, silent = False, origen = None, verbose = None):
        '''Escribe log en la pantalla, y si es error lo guarda en el Log'''

        origen = '' if origen is None else '{}: '.format(origen)

        # Guarda el log en el archivo
        if type == 'error':
            with open(log_file, 'a') as f:
                f.write('[{}] ERROR: {}{}\n'.format(datetime.now(), origen, repr(msg)))

        # Escribe en la pantalla
        if type == 'error' or not silent:
            print('{}{}{}'.format(
                Colors.style_str(type_list[type]['title'], type_list[type]['style']),
                origen,
                msg))
