#!/bin/sh
set -e

start_slurm

chmod go+rX -R /opt/karaage/
if test "$1" = "apache"
then
    chmod 644 /etc/apache2/conf-available/karaage3-wsgi.conf
fi

install -d -o www-data -g www-data /var/cache/karaage3
install -d -o www-data -g www-data /var/log/karaage3
install -d -o www-data -g www-data /var/lib/karaage3/files
install -d -o root -g root /var/lib/karaage3/static

python3 manage.py collectstatic --noinput

if test "$1" = "apache"
then
    install -d -o www-data -g www-data /var/log/apache2
    install -d -o _shibd -g _shibd /var/log/shibboleth
    ./scripts/start.sh "$@"
else
    sudo -u www-data -E ./scripts/start.sh "$@"
fi
