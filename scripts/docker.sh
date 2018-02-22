#!/bin/sh
set -e

chmod go+rX -R /opt/karaage/
if test "$1" = "apache"
then
    chmod 644 /etc/apache2/conf-available/karaage3-wsgi.conf
fi

if getent passwd munge > /dev/null
then
    echo "www-data ALL=(slurm) NOPASSWD: /usr/local/bin/sacct" >> /etc/sudoers
    echo "www-data ALL=(slurm) NOPASSWD: /usr/local/bin/sacctmgr" >> /etc/sudoers
    service munge start
fi

if ! test -d /var/cache/karaage3
then
    mkdir /var/cache/karaage3
    chown www-data:www-data /var/cache/karaage3
fi

if ! test -d /var/lib/karaage3/static
then
    mkdir -p /var/lib/karaage3/static
fi
python3 manage.py collectstatic --noinput

if test "$1" = "apache"
then
    ./scripts/start.sh "$@"
else
    sudo -u www-data -E ./scripts/start.sh "$@"
fi
