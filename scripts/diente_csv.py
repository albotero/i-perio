#!/usr/bin/env python3

import csv

csv_file = 'resources/bordes_dientes.csv'

def coord(num_diente, area, superior, implante, linea_0):
    '''Obtiene las coordenadas del diente en un mapa
        { y : [left_diente, centro_diente, right_diente]  }'''
    res = []
    with open(csv_file) as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if int(row['diente']) == num_diente:
                if row['area'] == area[1]:
                    # Borde superior
                    res += [int(row['top']), {}]
                    for i in range(22):
                        # Lee datos
                        raiz = (superior and i <= linea_0) or (not superior and i >= linea_0)

                        if implante and raiz:
                            left_diente = row['izq_impl'.format(i)]
                            right_diente = row['der_impl'.format(i)]
                        else:
                            left_diente = row['izq_{}'.format(i)]
                            right_diente = row['der_{}'.format(i)]

                        # Convierte a int
                        left_diente = int(left_diente) if left_diente.isnumeric() else 0
                        right_diente = int(right_diente) if right_diente.isnumeric() else 0
                        centro_diente = int((left_diente + right_diente) / 2)

                        # Datos de x
                        res[1][i] = [left_diente, centro_diente, right_diente]
    return res
