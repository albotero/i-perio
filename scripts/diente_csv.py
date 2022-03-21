#!/usr/bin/env python3

import csv

csv_file = 'resources/bordes_dientes.csv'

def coord(num_diente, area, img_width, espacio):
    '''Obtiene las coordenadas del diente en un mapa
        { y : [0, left_diente, centro_diente, right_diente, width]  }'''
    res = []
    with open(csv_file) as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if int(row['diente']) == num_diente:
                if row['area'] == area[1]:
                    # Borde superior
                    res.append(int(row['top']))
                    res += [{}]
                    for i in range(22):
                        left_diente = int(row['izq_{}'.format(i)])
                        right_diente = int(row['der_{}'.format(i)])
                        centro_diente = int((left_diente + right_diente) / 2)

                        # Datos de x
                        res[1][i * espacio] = [left_diente, centro_diente, right_diente]
    return res
