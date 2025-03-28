#!/bin/sh
set -ex

start_slurm

install -d -o www-data -g www-data /var/cache/karaage3
install -d -o www-data -g www-data /var/log/karaage3
install -d -o www-data -g www-data /var/lib/karaage3/files
install -d -o root -g root /var/lib/karaage3/static

if test "$1" = "root"; then
    shift
    uv run "$@"
else
    uv run python3 manage.py collectstatic --noinput
    sudo -u www-data -E "$@"
fi
