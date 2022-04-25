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

        # Agrega la fila de gastos a la tabla
        gastos = {
            'id_usuario': self['id_usuario'],
            'gastado': 0
        }
        res = self.guardar_datos('gastos', dict_valores=gastos)
        if res is None or res == 0:
            self['error'] = (f'Error al crear la el registro de gastos en la tabla `cr&eacute;ditos`.')
            return

        return nuevousuario.get("email")


    def obtener_creditos(self, descontar_credito = False):
        '''Evalúa el número de créditos disponibles que tiene el usuario,
            y descuenta uno si descontar_credito es True'''

        if descontar_credito:
            comando = f'''
                UPDATE `gastos`
                SET `gastado` = `gastado` + {valor_credito}
                WHERE `id_usuario` = {self.get("id_usuario")};
                '''
            ejecutar_mysql(comando, origen='usuarios.obtener_creditos')

        comando = f'''
            SELECT
                g.`id_usuario`
                `recargas`,
                g.`gastado`,
                (`recargas` - g.`gastado`) / {valor_credito} AS `restante_creditos`
            FROM
                (SELECT
                    c.`id_usuario`,
                    SUM(
                        CASE WHEN c.`estado` = 'approved'
                        THEN c.`monto`
                        ELSE 0
                        END
                    ) AS `recargas`
                FROM `creditos` c
                WHERE c.`id_usuario` = {self.get("id_usuario")}
                ) AS tabla
                INNER JOIN `gastos` g
                WHERE g.`id_usuario` = {self.get("id_usuario")};
            '''

        rows, valores, _ = ejecutar_mysql(comando, origen='usuarios.obtener_creditos')

        if (valores is None or
            valores[0].get('recargas') is None or
            valores[0].get('restante_creditos') is None):
            # El usuario no tiene ninguna transacción
            return 0

        valores = [ x.get('restante_creditos') for x in valores ]

        creditos = int(sum(valores))

        if creditos < 0:
            comando = f'''
                UPDATE `gastos` AS r
                JOIN (
                    SELECT
                        `id_usuario`,
                        SUM(`monto`) AS `sum_monto`
                    FROM `creditos`
                    WHERE `id_usuario` = {self.get("id_usuario")}
                        AND `estado` = 'approved'
                    ) AS grp
                ON grp.id_usuario = r.id_usuario
                SET `gastado` = grp.sum_monto
                WHERE `id_usuario` = {self.get("id_usuario")};
                '''
            ejecutar_mysql(comando, origen='usuarios.obtener_creditos')
            return 0

        return creditos


    dict_pago = {
        'tipo_pago': {
            'account_money': 'Mercado Pago',
            'ticket': 'Ticket',
            'bank_transfer': 'Transferencia bancaria',
            'atm': 'Pago en ATM',
            'credit_card': 'T. Cr&eacute;dito',
            'debit_card': 'T. D&eacute;bito',
            'prepaid_card': 'T. Prepaga'
        },
        'metodo_pago': {
            '': ''
        },
        'estado': {
            'pending': 'Pendiente',
            'approved': 'Aprobado',
            'authorized': 'Autorizado',
            'in_process': 'En revisi&oacute;n',
            'in_mediation': 'En disputa',
            'rejected': 'Rechazado',
            'cancelled': 'Cancelado',
            'refunded': 'Reembolsado',
            'charged_back': 'Reversado'
        },
        'detalle_estado': {
            'accredited': 'Pago acreditado',
            'pending_contingency': 'El pago est&aacute; siendo procesado',
            'pending_review_manual': 'El pago est&aacute; en revisi&oacute;n',
            'pending_waiting_payment': 'Esperando que se realice el pago',
            'cc_rejected_bad_filled_date': 'Fecha de vencimiento incorrecta',
            'cc_rejected_bad_filled_other': 'Datos de la tarjeta incorrectos',
            'cc_rejected_bad_filled_security_code': 'CVV incorrecto',
            'cc_rejected_blacklist': 'Tarjeta bloqueada por robo/denuncias/fraude',
            'cc_rejected_call_for_authorize': 'Requiere autorizar previamente el monto',
            'cc_rejected_card_disabled': 'Tarjeta encuentra inactiva',
            'cc_rejected_duplicated_payment': 'Transacci&oacute;n duplicada',
            'cc_rejected_high_risk': 'Rechazo por Prevenci&oacute;n de Fraude',
            'cc_rejected_insufficient_amount': 'Monto insuficiente',
            'cc_rejected_invalid_installments': 'N&uacute;mero de cuotas inv&aacute;lidas',
            'cc_rejected_max_attempts': 'Super&oacute; m&aacute;ximo de intentos',
            'cc_rejected_other_reason': 'Error gen&eacute;rico'
        }
    }


    def diccionario_pago(self, key, dicc):
        return self.dict_pago[key].get(dicc[key], dicc[key])


    def obtener_transacciones(self):
        comando = f'''
            SELECT *
            FROM `creditos`
            WHERE `id_usuario` = {self.get("id_usuario")}
            ORDER BY `fecha_transaccion` DESC;
            '''
        rows, valores, _ = ejecutar_mysql(comando, origen='usuarios.obtener_transacciones')
        if rows is None or rows == 0:
            return

        for transaccion in valores:
            tipo = self.diccionario_pago('tipo_pago', transaccion)
            metodo = self.diccionario_pago('metodo_pago', transaccion)
            transaccion['medio_pago'] = f'{tipo}<br/>{metodo}'

            transaccion['_estado'] = self.diccionario_pago('estado', transaccion)
            transaccion['detalle_estado'] = self.diccionario_pago('detalle_estado', transaccion)

        return valores


    def registrar_pago(self, transaccion, fecha_transaccion, estado,
                        detalle_estado, tipo_pago, metodo_pago, monto):
        comando = f'''
            INSERT INTO `creditos`
                (`transaccion`, `id_usuario`, `fecha_transaccion`, `estado`,
                `detalle_estado`, `tipo_pago`, `metodo_pago`, `monto`)
            VALUES
                ("{transaccion}", "{self['id_usuario']}", "{fecha_transaccion}", "{estado}",
                "{detalle_estado}", "{tipo_pago}", "{metodo_pago}", "{monto}")
            ON DUPLICATE KEY UPDATE
                `fecha_transaccion`="{fecha_transaccion}",
                `estado`="{estado}",
                `detalle_estado`="{detalle_estado}",
                `tipo_pago`="{tipo_pago}",
                `metodo_pago`="{metodo_pago}",
                `monto`="{monto}";
            '''
        rows, _, _ = ejecutar_mysql(comando, origen='usuarios.registrar_pago')


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
