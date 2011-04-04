#!/bin/bash

# Sets secret key if doesn't exist

if grep "SECRET_KEY = ''" /etc/karaage/global_settings.py &> /dev/null
    then /usr/sbin/kg_set_secret_key
fi

# Create cache directory
mkdir -p /var/cache/karaage/
