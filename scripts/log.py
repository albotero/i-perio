from .colors import Colors

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

    def out(msg, type, silent = False):
        # Guarda el log en el archivo

        # Escribe en la pantalla
        if not silent:
            print(Colors.style_str(type_list[type]['title'], type_list[type]['style']) + msg)
