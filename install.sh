#!/bin/bash
# start with sudo

apt update
apt upgrade -y

# instalar dependencias
apt install -y python3 python3-dev mysql-server libvirt-dev python3-mysqldb python-cairo

# directorio de trabajo
cd /var/www/i-perio

# actualiza la app
git pull

# instalar módulos
cat requirements.txt | grep -Eo '(^[^#]+)' | xargs -n 1 pip3 install

# crear la base de datos
mysql -e "CREATE USER iperio@localhost IDENTIFIED BY 'contrasena'; GRANT ALL PRIVILEGES ON *.* TO iperio@localhost;"
mysql -u iperio -p < sql/basedatos.sql

# reinicia los servicios
systemctl restart nginx
systemctl restart i-perio
