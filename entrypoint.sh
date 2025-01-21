#!/bin/bash

python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
gunicorn -k uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:8000 simulateagents.asgi:application
#python manage.py runserver 0.0.0.0:8000