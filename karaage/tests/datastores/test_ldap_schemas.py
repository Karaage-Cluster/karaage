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

from karaage.tests.fixtures import AccountFactory
from karaage.tests.integration import IntegrationTestCase


class OpenldapAccountTestCase(IntegrationTestCase):

    def setUp(self):
        super(OpenldapAccountTestCase, self).setUp()

    def test_kAccountMixin(self):
        account = AccountFactory()
        ldap = self._ldap_datastore._accounts()
        self._ldap_datastore.save_account(account)
        ldap_account = ldap.get(uid=account.username)
        self.assertEqual(
            ldap_account.uid,
            account.username
        )
