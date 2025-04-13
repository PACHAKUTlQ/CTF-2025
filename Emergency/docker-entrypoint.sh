#!/bin/sh

if [ "$FLAG" ]; then
    INSERT_FLAG="$FLAG"
    export FLAG=no_FLAG
    FLAG=no_FLAG
else
    INSERT_FLAG="0ops{test}"
fi

echo $INSERT_FLAG | tee /flag

chmod 744 /flag

cd /app & npm run start
sleep infinity