# Copyright 2014-2015 VPAC
# Copyright 2014 The University of Melbourne
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

import six

from karaage.tests.integration import IntegrationTestCase
from karaage.tests.fixtures import PersonFactory


class OpenldapPersonTestCase(IntegrationTestCase):

    def setUp(self):
        self.LDAP_CONFIG['PERSON'] = \
            'karaage.datastores.ldap_schemas.openldap_person'
        super(OpenldapPersonTestCase, self).setUp()

    def test_kAccountMixin(self):
        person = PersonFactory()
        ldap = self.global_ldap_datastore._people()
        self.global_ldap_datastore.save_person(person)
        ldap_person = ldap.get(uid=person.username)
        self.assertEqual(
            ldap_person.displayName,
            six.u('%s (%s)') % (person.full_name, person.institute))
