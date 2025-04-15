#!/bin/bash

sqlite3 /app/ezlogin.db < /app/db.sql
RANDOM_PW=$(openssl rand -hex 16)
sqlite3 /app/ezlogin.db "UPDATE users SET password='$RANDOM_PW' WHERE id=2;"

chown -R www-data /app
chmod -R 777 /app

source /etc/apache2/envvars

echo "Running..." &

tail -F /var/log/apache2/* &

exec apache2 -D FOREGROUND