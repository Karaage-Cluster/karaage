#!/bin/sh
set -e
echo "www-data ALL=(slurm) NOPASSWD: /usr/local/bin/sacct" >> /etc/sudoers

if getent passwd munge > /dev/null
then
    service munge start
fi

if ! test -d /var/lib/karaage3
then
    mkdir /var/lib/karaage3
    chown www-data:www-data /var/lib/karaage3
fi

if ! test -d /var/cache/karaage3
then
    mkdir /var/cache/karaage3
    chown www-data:www-data /var/cache/karaage3
fi

sudo -u www-data ./scripts/start.sh
