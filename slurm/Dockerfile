# Start with a Python image.
FROM python:3.6-stretch as slurm
MAINTAINER brian@linuxpenguins.xyz

# Slurm configuration
ARG SLURM_VER=17.02.7
ARG SLURM_URL=https://www.schedmd.com/downloads/latest/slurm-17.02.7.tar.bz2

# Install OS dependencies
RUN apt-get update \
  && apt-get install -y \
    bzip2 make gcc libmunge-dev liblua5.3-dev \
  && rm -rf /var/lib/apt/lists/*

# Build and install slurm
RUN curl -fsL ${SLURM_URL} | tar xfj - -C /opt/ && \
    cd /opt/slurm-${SLURM_VER}/ && \
    ./configure && make && make install
VOLUME ["/etc/munge", "/usr/local/etc", "/var/lib/munge", "/var/log/munge"]


# Start with a Python image.
FROM python:3.6-stretch
MAINTAINER brian@linuxpenguins.xyz

# Install OS dependencies
RUN apt-get update \
  && apt-get install -y \
    gcc munge liblua5.3-0 \
  && rm -rf /var/lib/apt/lists/*

COPY --from=slurm /usr/local /usr/local
VOLUME ["/etc/munge", "/usr/local/etc", "/var/lib/munge", "/var/log/munge"]
