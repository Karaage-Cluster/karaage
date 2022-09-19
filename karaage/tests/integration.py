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
import os
from unittest import skipUnless

import pkg_resources
import tldap.database
import tldap.transaction
from django.test import TestCase

from karaage.datastores import _DATASTORES
from karaage.datastores.ldap import DataStore
from karaage.middleware.threadlocals import reset


def skip_if_missing_requirements(*requirements):
    try:
        pkg_resources.require(*requirements)
        msg = ""
    except pkg_resources.DistributionNotFound:
        msg = "Missing one or more requirements (%s)" % "|".join(requirements)
    return skipUnless(msg == "", msg)


class IntegrationTestCase(TestCase):
    LDAP_CONFIG = {
        "DESCRIPTION": "LDAP datastore",
        "ENGINE": "karaage.datastores.ldap.AccountDataStore",
        "LDAP": "default",
        "PRIMARY_GROUP": "institute",
        "DEFAULT_PRIMARY_GROUP": "dummy",
        "NUMBER_SCHEME": "default",
        "LDAP_ACCOUNT_BASE": os.environ["LDAP_ACCOUNT_BASE"],
        "LDAP_GROUP_BASE": os.environ["LDAP_GROUP_BASE"],
        "HOME_DIRECTORY_FORMAT": "/vpac/{default_project}/{uid}",
        "GECOS_FORMAT": "{cn} ({o})",
    }

    def setUp(self):
        super(IntegrationTestCase, self).setUp()

        tldap.transaction.enter_transaction_management()

        self.addCleanup(self.cleanup)

        if os.environ["LDAP_TYPE"] == "openldap":
            config = {
                **self.LDAP_CONFIG,
                "ACCOUNT": "karaage.datastores.ldap_schemas.OpenldapAccount",
                "GROUP": "karaage.datastores.ldap_schemas.OpenldapGroup",
            }
        elif os.environ["LDAP_TYPE"] == "ds389":
            config = {
                **self.LDAP_CONFIG,
                "ACCOUNT": "karaage.datastores.ldap_schemas.Ds389Account",
                "GROUP": "karaage.datastores.ldap_schemas.Ds389Group",
            }
        else:
            raise RuntimeError(f"Unknown databasebase type {os.environ['LDAP_TYPE']}.")

        self._ldap_datastore = DataStore(config)

        database = self._ldap_datastore._database
        account = self._ldap_datastore._account_class(
            {
                "uid": "kgtestuser3",
                "givenName": "Test",
                "sn": "User3",
                "cn": "Test User3",
                "gidNumber": 500,
                "o": "Example",
            }
        )
        tldap.database.insert(account, database=database)

        group = self._ldap_datastore._group_class(
            {
                "cn": "Example",
                "gidNumber": 500,
            }
        )
        tldap.database.insert(group, database=database)

        group = self._ldap_datastore._group_class(
            {
                "cn": "otherinst",
                "gidNumber": 501,
            }
        )
        tldap.database.insert(group, database=database)

        group = self._ldap_datastore._group_class(
            {
                "cn": "TestProject1",
                "memberUid": ["kgtestuser3"],
                "gidNumber": 504,
            }
        )
        tldap.database.insert(group, database=database)

        _DATASTORES.clear()
        _DATASTORES.append(self._ldap_datastore)

    def cleanup(self):
        tldap.transaction.rollback()
        tldap.transaction.leave_transaction_management()

        reset()
        _DATASTORES.clear()
