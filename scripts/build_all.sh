#!/bin/sh
set -e

docker build \
    --file "Dockerfile" \
    --tag "brianmay/karaage:slurm16.05" \
    --build-arg="SLURM_VER=16.05" \
    .

docker build \
    --file "Dockerfile.apache" \
    --tag "brianmay/karaage:slurm16.05-apache" \
    --build-arg="SLURM_VER=16.05" \
    .
