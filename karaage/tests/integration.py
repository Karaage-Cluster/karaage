# Copyright 2014 The University of Melbourne
# Copyright 2007-2013 VPAC
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

from django.core.management import call_command
from django.test import TestCase
from tldap.test import slapd

from karaage.tests.initial_ldap_data import test_ldif
from karaage.datastores import _MACHINE_CATEGORY_DATASTORES, _GLOBAL_DATASTORES
from karaage.datastores.ldap import MachineCategoryDataStore, GlobalDataStore

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
    'LDAP_ACCOUNT_BASE': 'ou=People,dc=python-ldap,dc=org',
    'LDAP_GROUP_BASE': 'ou=Group,dc=python-ldap,dc=org',
}

GLOBAL_LDAP_CONFIG = {
    'DESCRIPTION': 'LDAP datastore',
    'ENGINE': 'karaage.datastores.ldap.GlobalDataStore',
    'LDAP': 'default',
    'PERSON': 'karaage.datastores.ldap_schemas.openldap_person',
    'GROUP': 'karaage.datastores.ldap_schemas.openldap_person_group',
    'LDAP_PERSON_BASE': 'ou=People,dc=python-ldap,dc=org',
    'LDAP_GROUP_BASE': 'ou=Group,dc=python-ldap,dc=org',
}

class IntegrationTestCase(TestCase):
    ldap_datastore = 'ldap'

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        server = slapd.Slapd()
        server.set_port(38911)
        server.start()
        server.ldapadd("\n".join(test_ldif)+"\n")
        self.__ldap_server = server
        self.mc_ldap_datastore = MachineCategoryDataStore(LDAP_CONFIG)
        self.global_ldap_datastore = GlobalDataStore(GLOBAL_LDAP_CONFIG)
        _MACHINE_CATEGORY_DATASTORES[self.ldap_datastore] = [self.mc_ldap_datastore]
        # NOTE (RS) this is currently disabled because it causes test
        # failures.
        # _GLOBAL_DATASTORES.append(self.global_ldap_datastore)

    def tearDown(self):
        super(IntegrationTestCase, self).tearDown()
        self.__ldap_server.stop()
        _MACHINE_CATEGORY_DATASTORES[self.ldap_datastore] = []
        # _GLOBAL_DATASTORES.remove(self.global_ldap_datastore)
