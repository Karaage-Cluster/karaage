#!/bin/sh
set -e

./docker/start_db.sh

/usr/bin/docker run -ti \
  --name karaage \
  --rm \
  -p 8000:8000 \
  -v $PWD/docker/passwd:/etc/passwd \
  -v $PWD/docker/group:/etc/group \
  -v $PWD/docker/settings:/etc/karaage3 \
  -v $PWD/local/log:/var/log/karaage3 \
  --link karaage-mysql:mysql \
  --link karaage-redis:redis \
  brianmay/karaage:slurm16.05 "$@"

# other desirable parameters
#  --net="host" \
#  -v /etc/munge:/etc/munge \
#  -v /var/lib/munge:/var/lib/munge \
#  -v /var/log/munge:/var/log/munge \
#  -v /usr/local/slurm/etc:/usr/local/etc \
