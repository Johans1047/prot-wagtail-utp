#!/usr/bin/env bash
set -e

python3 manage.py collectstatic --noinput
python3 manage.py migrate --noinput

exec gunicorn mysite.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120