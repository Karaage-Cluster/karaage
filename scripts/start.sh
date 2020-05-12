#!/bin/bash
set -e

python3 manage.py migrate --noinput

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn karaage.wsgi:application \
    --log-file=- \
    --bind 0.0.0.0:8000 \
    --worker-tmp-dir /dev/shm \
    --workers 3
