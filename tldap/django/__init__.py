# Copyright 2012-2014 Brian May
#
# This file is part of python-tldap.
#
# python-tldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-tldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-tldap  If not, see <http://www.gnu.org/licenses/>.

""" Django function support. """

from __future__ import absolute_import

import django.conf

from tldap.backend import setup
from tldap.utils import DEFAULT_LDAP_ALIAS


default_app_config = 'tldap.django.apps.TldapConfig'

# For backwards compatibility - Port any old database settings over to
# the new values.
if not hasattr(django.conf.settings, 'LDAP'):
    django.conf.settings.LDAP = {}

# ok to use django settings
if not django.conf.settings.LDAP and hasattr(django.conf.settings, 'LDAP_URL'):
    django.conf.settings.LDAP[DEFAULT_LDAP_ALIAS] = {
        'ENGINE': 'tldap.backend.fake_transactions',
        'URI': django.conf.settings.LDAP_URL,
        'USER': django.conf.settings.LDAP_ADMIN_USER,
        'PASSWORD': django.conf.settings.LDAP_ADMIN_PASSWORD,
        'START_TLS': False,
        'TLS_CA': None,
        'LDAP_ACCOUNT_BASE': django.conf.settings.LDAP_USER_BASE,
        'LDAP_GROUP_BASE': django.conf.settings.LDAP_GROUP_BASE,
    }
    if hasattr(django.conf.settings, 'LDAP_USE_TLS'):
        django.conf.settings.LDAP[DEFAULT_LDAP_ALIAS]["START_TLS"] = (
            django.conf.settings.LDAP_USE_TLS)
    django.conf.settings.LDAP[DEFAULT_LDAP_ALIAS]["TLS_CA"] = (
        django.conf.settings.LDAP_TLS_CA)

setup(django.conf.settings.LDAP)
