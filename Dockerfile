ARG SLURM_VER=17.02
FROM brianmay/slurm:${SLURM_VER}
MAINTAINER brian@linuxpenguins.xyz

# Install OS dependencies
RUN apt-get update \
  && apt-get install -y \
    gcc sudo libcrack2-dev \
  && rm -rf /var/lib/apt/lists/*

# Make application directory
RUN mkdir /opt/karaage /opt/karaage/requirements
WORKDIR /opt/karaage

# Install our requirements.
ADD requirements/*.txt /opt/karaage/requirements/
RUN pip install -r requirements/docker.txt

# Copy all our files into the image.
COPY . /opt/karaage/
RUN chmod go+rX -R /opt/karaage/

# Setup access to version information
ARG BUILD_DATE=
ARG VCS_REF=
ENV BUILD_DATE=${BUILD_DATE}
ENV VCS_REF=${VCS_REF}
ENV SLURM_VER=${SLURM_VER}

# Specify the command to run when the image is run.
EXPOSE 8000
VOLUME '/etc/karaage3' '/var/log' '/var/lib/karaage3'
CMD /opt/karaage/scripts/docker.sh gunicorn
