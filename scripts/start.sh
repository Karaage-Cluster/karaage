#!/bin/bash
set -e

python3 manage.py migrate --noinput
#python3 manage.py celery worker --time-limit=300 --concurrency=1 --loglevel=INFO --logfile=/var/log/karaage3/w1.log -D

if test "$1" = "gunicorn"
then
    # Start Gunicorn processes
    echo Starting Gunicorn.
    exec gunicorn karaage.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 3

elif test "$1" = "apache"
then
    service shibd start
    /usr/sbin/apache2ctl -D FOREGROUND

fi
