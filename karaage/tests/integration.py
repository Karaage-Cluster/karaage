# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
#
# This file is part of Karaage.
#
# Karaage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Karaage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Karaage  If not, see <http://www.gnu.org/licenses/>.

from unittest import skipUnless

import pkg_resources
from django.test import TestCase
from tldap.test import slapd

from karaage.datastores import _DATASTORES
from karaage.datastores.ldap import DataStore
from karaage.middleware.threadlocals import reset
from karaage.tests.initial_ldap_data import test_ldif


def skip_if_missing_requirements(*requirements):
    try:
        pkg_resources.require(*requirements)
        msg = ''
    except pkg_resources.DistributionNotFound:
        msg = 'Missing one or more requirements (%s)' % '|'.join(requirements)
    return skipUnless(msg == '', msg)


class IntegrationTestCase(TestCase):
    LDAP_CONFIG = {
        'DESCRIPTION': 'LDAP datastore',
        'ENGINE': 'karaage.datastores.ldap.AccountDataStore',
        'LDAP': 'default',
        'ACCOUNT': 'karaage.datastores.ldap_schemas.openldap_account',
        'GROUP': 'karaage.datastores.ldap_schemas.openldap_account_group',
        'PRIMARY_GROUP': "institute",
        'DEFAULT_PRIMARY_GROUP': "dummy",
        'HOME_DIRECTORY': "/vpac/%(default_project)s/%(uid)s",
        'LOCKED_SHELL': "/usr/local/sbin/locked",
        'LDAP_ACCOUNT_BASE': 'ou=Account,dc=python-ldap,dc=org',
        'LDAP_GROUP_BASE': 'ou=Group,dc=python-ldap,dc=org',
    }

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        server = slapd.Slapd()
        server.set_port(38911)
        server.start()

        self.addCleanup(self.cleanup)

        server.ldapadd("\n".join(test_ldif) + "\n")
        self.__ldap_server = server
        self._ldap_datastore = DataStore(self.LDAP_CONFIG)
        _DATASTORES.clear()
        _DATASTORES.append(self._ldap_datastore)

    def cleanup(self):
        self.__ldap_server.stop()
        reset()
        _DATASTORES.clear()
