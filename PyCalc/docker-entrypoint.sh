#!/bin/sh

echo $FLAG | tee /flag

chmod 744 /flag
chmod 740 /app/*

cd /app && flask run -h 0.0.0.0 -p 8080