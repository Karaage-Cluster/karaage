#!/bin/sh
set -e

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

chown www-data:root -R /var/lib/karaage3/static
sudo -u www-data python3 manage.py collectstatic --noinput
chown root:root -R /var/lib/karaage3/static

sudo -u www-data ./scripts/start.sh
