#!/bin/sh

wait-for-it.sh localhost:5432
python3 manage.py makemigrations bnhs_users
python3 manage.py migrate bnhs_users
python3 manage.py makemigrations covid19_case_records
python3 manage.py migrate covid19_case_records
python3 manage.py migrate
python3 manage.py collectstatic --noinput

python3 manage.py

exec "$@"