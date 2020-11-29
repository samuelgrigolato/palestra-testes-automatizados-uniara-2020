#!/bin/bash

trap "kill 0" EXIT

set -e

rm -f app.db

source ../back/venv/bin/activate
PYTHONPATH=../back python -m flask run &
sleep 2 # dê um tempo para ele inicializar
curl http://localhost:5000/ping
sqlite3 app.db "insert into produtos (id, nome, valor_em_centavos) values (1, 'Bala', 300);"

cd ../front
BROWSER=none npm start &
cd ../e2e
sleep 2

python e2e.py
