from diente import Diente

def crear_diente(indice, pediatrico):
    '''Crea un nuevo Diente, el número del diente lo toma según el índice'''
    cuadrante = indice // 8 + 1
    diente = indice % 8 + 1

    #Invierte los cuadrantes 3 y 4 para que primero sea 4 y luego 3
    if cuadrante == 3:
        cuadrante = 4
    elif cuadrante == 4:
        cuadrante = 3

    #En los cuadrantes 1 y 4 el conteo se enumera de 8 a 1
    if cuadrante == 1 or cuadrante == 4:
        diente = 9 - diente

    #Obtiene el número del diente según el cuadrante
    numero_diente = cuadrante * 10 + diente

    if pediatrico:
        numero_diente += 40
        #La dentición decidua solo tiene hasta 5 dientes
        if diente > 5:
            return

    return Diente(numero_diente)

def nuevo_perio(pediatrico = False):
    '''Inicializa un nuevo periodontograma'''
    perio = {}
    for i in range(32):
        nuevo_diente = crear_diente(i, pediatrico)
        if nuevo_diente is not None:
            perio[nuevo_diente.diente] = nuevo_diente
    return perio

def __main__():
    '''Clase principal desde la cual se genera el periodontograma'''
    perio = nuevo_perio()
    print(perio.keys())

__main__()
