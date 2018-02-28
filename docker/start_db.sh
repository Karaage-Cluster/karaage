#!/bin/sh
set -e
if [ ! "$(docker ps -q -f name=karaage-mysql)" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=karaage-mysql)" ]; then
        # cleanup
        docker rm karaage-mysql
    fi
    # run your container
    docker run --rm --name karaage-mysql -e MYSQL_ROOT_PASSWORD=q1w2e3r4 -d mysql
    docker run -ti \
        --rm \
        -v $PWD/docker/mysql.conf:/root/.my.cnf \
        --link karaage-mysql:mysql \
        mysql \
        mysql -e "CREATE DATABASE IF NOT EXISTS karaage;"
fi
if [ ! "$(docker ps -q -f name=karaage-redis)" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=karaage-redis)" ]; then
        # cleanup
        docker rm karaage-redis
    fi
    # run your container
    docker run --rm --name karaage-redis -d redis
fi

