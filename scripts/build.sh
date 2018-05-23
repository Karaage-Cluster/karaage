#!/bin/sh
set -e

docker build \
    --file "Dockerfile" \
    --tag "brianmay/karaage:slurm17.02" \
    --build-arg="SLURM_VER=17.02" \
    --build-arg "BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"`" \
    --build-arg "VCS_REF=`git rev-parse --short HEAD`" \
    .
