#!/bin/sh
set -e

docker build \
    --file "Dockerfile" \
    --tag "brianmay/karaage:slurm16.05" \
    --build-arg="SLURM_VER=16.05" \
    --build-arg "BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"`" \
    --build-arg "VCS_REF=`git rev-parse --short HEAD`" \
    .

