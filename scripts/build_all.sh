#!/bin/sh
set -e
docker build \
    --tag "brianmay/slurm:16.05" \
    --build-arg="SLURM_VER=16.05.10" \
    --build-arg="SLURM_URL=https://www.schedmd.com/downloads/archive/slurm-16.05.10.tar.bz2" \
    slurm

docker build \
    --file "Dockerfile" \
    --tag "brianmay/karaage:slurm16.05" \
    --build-arg="SLURM_VER=16.05" \
    .
