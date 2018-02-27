#!/bin/bash
set -e

python3 manage.py migrate --noinput
python3 -m celery -A karaage.celery worker \
    --concurrency=1 \
    --loglevel=INFO \
    --pidfile=/var/run/lock/celery.pid \
    --logfile=/var/log/karaage3/celery.log \
    --detach
python3 -m celery -A karaage.celery beat \
    --schedule /tmp/celerybeat-schedule \
    --loglevel=INFO \
    --pidfile=/var/run/lock/beat.pid \
    --logfile=/var/log/karaage3/beat.log \
    --detach

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
