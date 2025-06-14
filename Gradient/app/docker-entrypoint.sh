#!/bin/bash

source /etc/apache2/envvars

echo "Running..." &

tail -F /var/log/apache2/* &

exec apache2 -D FOREGROUND