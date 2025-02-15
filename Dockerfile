ARG SLURM_VER=24.05
FROM brianmay/slurm:${SLURM_VER}

# Install OS dependencies
RUN apt-get update \
  && apt-get install -y \
  gcc sudo libcrack2-dev netcat \
  && rm -rf /var/lib/apt/lists/*

# Make application directory
RUN mkdir /opt/karaage /opt/karaage/requirements
WORKDIR /opt/karaage

# Install our requirements.
RUN pip install poetry==1.3.0
ADD pyproject.toml poetry.lock /opt/karaage/
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-root

# Copy all our files into the image.
COPY . /opt/karaage/
RUN chmod go+rX -R /opt/karaage/

# Setup access to version information
ARG VERSION=
ARG BUILD_DATE=
ARG VCS_REF=
ENV VERSION=${VERSION}
ENV BUILD_DATE=${BUILD_DATE}
ENV VCS_REF=${VCS_REF}

ENV KARAAGE_CONFIG_FILE=/etc/karaage3/settings.py

# Specify the command to run when the image is run.
EXPOSE 8000
VOLUME '/etc/karaage3' '/var/log' '/var/lib/karaage3' '/var/cache/karaage3'
ENTRYPOINT [ "/opt/karaage/scripts/docker.sh" ]
CMD /opt/karaage/scripts/start.sh
