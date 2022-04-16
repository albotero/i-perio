#!/usr/bin/env python3

from .log import Log
from datetime import datetime
import hashlib
import os
import MySQLdb


base_datos = 'iperio'
usuario = 'iperio'
host = 'localhost'
contrasena = 'contrasena'

# 60 minutos valen COP 5000
valor_credito = 5000 / 60;

def ejecutar_mysql(comando, origen='usuarios.ejecutar_mysql'):
    dbconnect = MySQLdb.connect(host, usuario, contrasena, base_datos)
    cursor = dbconnect.cursor(MySQLdb.cursors.DictCursor)
    rows, data, id_usuario = None, None, None
    try:
        rows = cursor.execute(comando)
        data = cursor.fetchall()
        id_usuario = cursor.lastrowid
        dbconnect.commit()
    except Exception as ex:
        Log.out(ex, 'error', silent=False, origen=origen)
        dbconnect.rollback()
    finally:
        dbconnect.close()
        return rows, data, id_usuario

class Usuario (dict):

    def obtener_id_usuario(self, email):
        '''Obtiene el ID del usuario según el email'''
        comando = f'SELECT `id_usuario` FROM `usuarios` WHERE `email` = "{email}";'
        rows, valores, _ = ejecutar_mysql(comando, origen='usuarios.Usuario.obtener_id_usuario')
        if rows == 0:
            self['error'] = (f'El correo electrónico <span style="font-weight: bold;">'
                            + f'{email}</span> no se encuentra registrado.')
            return
        return valores[0]['id_usuario']


    def cargar_datos(self, tabla):
        '''Carga los datos desde la BD al diccionario self'''
        comando = f'SELECT * FROM `{tabla}` WHERE `id_usuario` = {self["id_usuario"]};'
        rows, valores, _ = ejecutar_mysql(comando, origen='usuarios.cargar_datos')
        if rows == 0:
            Log.out(f'id_usuario {self["id_usuario"]}: No se cargaron datos de la tabla `{tabla}` de la BD',
                    'error', silent=False, origen='usuarios.Usuario.cargar_datos')
            return
        # Agrega los valores leidos al dict
        self[tabla] = valores[0]


    def guardar_datos(self, tabla, update = False, dict_valores = None):
        '''Guarda los valores de self[tabla] en la base de datos'''
        if dict_valores is None:
            dict_valores = self[tabla]

        if update:
            valores = ''
            for dato, valor in dict_valores.items():
                valores += f', `{dato}`="{valor}"'
            comando = f'UPDATE `{tabla}` SET {valores[2:]} WHERE `id_usuario` = {self["id_usuario"]};'
        else:
            columnas = ', '.join([f'`{col}`' for col in dict_valores.keys() ])
            valores = ', '.join([f'\'{val}\'' for val in dict_valores.values() ])
            comando = f'INSERT INTO `{tabla}` ({columnas}) VALUES ({valores});'

        rows, _, self['id_usuario'] = ejecutar_mysql(comando, origen='usuarios.guardar_datos')

        if rows == 0:
            Log.out(f'id_usuario {self["id_usuario"]}: No se guardaron datos en la tabla `{tabla}` de la BD',
                    'error', silent=False, origen='usuarios.Usuario.guardar_datos')

        return rows


    def hash_contrasena(self, contrasena, salt = os.urandom(32)):
        try:
            key = hashlib.pbkdf2_hmac(
                'sha256', # The hash digest algorithm for HMAC
                contrasena.encode('utf-8'), # Convert the password to bytes
                salt, # Provide the salt
                100000 # It is recommended to use at least 100,000 iterations of SHA-256
            )
            return f'{salt.hex()}{key.hex()}'
        except Exception as ex:
            Log.out(f'id_usuario {self["id_usuario"]}: {ex}',
                    'error', silent=False, origen='usuarios.hash_contrasena')


    def comprobar_contrasena(self, contrasena):
        '''Evalúa si la contraseña administrada coincide con la guardada en la BD'''
        if self['usuarios']['key'] is None:
            # No tiene una contraseña
            return False

        # Valida la contraseña
        salt = bytes.fromhex(self['usuarios']['key'][:64])
        new = self.hash_contrasena(contrasena, salt)
        return self['usuarios']['key'] == new


    def crear_usuario(self, nuevousuario):
        '''Crea un nuevo usuario con los datos del diccionario'''
        self['usuarios'] = nuevousuario

        # Si no se especificó un correo, no hace nada
        if nuevousuario.get("email") is None:
            return

        # Evalúa si el email ya existe
        comando = f'SELECT * FROM `usuarios` WHERE `email` = "{nuevousuario.get("email")}";'
        rows, _, _ = ejecutar_mysql(comando, origen='usuarios.crear_usuario')
        if rows is not None and rows > 0:
            self['error'] = (f'El correo electrónico <span style="font-weight: bold;">'
                            + f'{nuevousuario.get("email")}</span> ya se encuentra registrado.')
            return

        # Si no se administró una contraseña, crea una por defecto: 123456
        self['usuarios']['key'] = self.hash_contrasena(nuevousuario.get('key','123456'))
        self['usuarios']['creacion'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        res = self.guardar_datos('usuarios')
        if res is None or res == 0:
            self['error'] = (f'Ocurri&oacute; un error al registrar el usuario.<br />'
                            +f'Por favor contacte al administrador - [usuarios.Usuario.crear_usuario].')
            return

        return nuevousuario.get("email")


    def obtener_creditos(self, descontar_credito = False):
        '''Evalúa el número de créditos disponibles que tiene el usuario,
            y descuenta uno si descontar_credito es True'''

        if descontar_credito:
            comando = f'''
                UPDATE `creditos`
                SET `gastado_cop` = `gastado_cop` + {valor_credito}
                WHERE `id_usuario` = {self["id_usuario"]} AND `numero_transaccion` = "gastos";
                '''
            ejecutar_mysql(comando, origen='usuarios.obtener_creditos')

        comando = f'''
            SELECT (
                (SUM(`monto_cop`)-SUM(`gastado_cop`)) / {valor_credito}
            ) as `restante_creditos`
            FROM `creditos` WHERE `id_usuario` = {self["id_usuario"]};
            '''
        rows, valores, _ = ejecutar_mysql(comando, origen='usuarios.obtener_creditos')

        if rows == 0:
            # El usuario no tiene ninguna transacción
            return 0

        valores = [ x['restante_creditos'] for x in valores ]

        creditos = int(sum(valores))

        if creditos < 0:
            comando = f'''
                UPDATE `creditos`'
                SET `gastado_cop` = SUM(SELECT(`monto_cop` WHERE `id_usuario` = {self["id_usuario"]}))'
                WHERE `id_usuario` = {self["id_usuario"]} AND `numero_transaccion` = "gastos";
                '''
            ejecutar_mysql(comando, origen='usuarios.obtener_creditos')
            return 0

        return creditos


    def __init__ (self, email = None, id_usuario = None, nuevousuario = {}):
        '''Si existe el usuario carga los datos de la BD, si no, crea uno nuevo'''

        if email is None and id_usuario is None: # Debe crear un nuevo usuario
            email = self.crear_usuario(nuevousuario)
            if email is None: # No pudo crear el nuevo usuario
                return

        if id_usuario is not None:
            self['id_usuario'] = id_usuario
        else:
            self['id_usuario'] = self.obtener_id_usuario(email)

        if self.get('id_usuario'):
            self.cargar_datos('usuarios')
