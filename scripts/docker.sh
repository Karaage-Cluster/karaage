#!/bin/sh
set -e
echo "www-data ALL=(slurm) NOPASSWD: /usr/local/bin/sacct" >> /etc/sudoers
service munge start
mkdir /var/lib/karaage3
chown www-data:www-data /var/lib/karaage3
mkdir /var/cache/karaage3
chown www-data:www-data /var/cache/karaage3
sudo -u www-data ./scripts/start.sh
