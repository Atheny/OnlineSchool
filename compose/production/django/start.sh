#!/bin/bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
#python manage.py runserver 0.0.0.0:8000
gunicorn OnlineSchool.wsgi:application -w 2 -k gthread -b 0.0.0.0:8000 --chdir=/app/OnlineSchool