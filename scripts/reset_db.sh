#!/bin/bash

rm -rf "api/migrations" "db.sqlite3"
python manage.py makemigrations api
python manage.py migrate --fake-initial api

python manage.py migrate
python manage.py populate_db
