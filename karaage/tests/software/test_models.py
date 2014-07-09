# Copyright 2007-2014 VPAC
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

import mock

from karaage.tests.unit import UnitTestCase
from karaage.tests.fixtures import (SoftwareFactory, simple_account,
                                    GroupFactory)


class SoftwareTestCase(UnitTestCase):

    def test_change_group(self):
        """Check that when changing an software group, old accounts are
        removed from the software and new ones are added.

        """
        account1 = simple_account(machine_category=self.machine_category)
        group1 = GroupFactory()
        group1.add_person(account1.person)

        # Test during initial creation of the software
        self.resetDatastore()
        software = SoftwareFactory(group=group1)
        self.assertEqual(
            self.datastore.method_calls,
            [mock.call.save_software(software),
                mock.call.add_account_to_software(account1, software)])

        # Test changing an existing software group
        account2 = simple_account(machine_category=self.machine_category)
        self.resetDatastore()
        group2 = GroupFactory()
        group2.add_person(account2.person)
        software.group = group2
        software.save()
        self.assertEqual(
            self.datastore.method_calls,
            [mock.call.save_group(group2),
             mock.call.add_account_to_group(account2, group2),
             mock.call.save_software(software),
             # old accounts are removed
             mock.call.remove_account_from_software(account1, software),
             # new accounts are added
             mock.call.add_account_to_software(account2, software)])

        # Test removing the group
        #
        # Test is currently broken, as the save() operation will give the
        # software a group if none is given. This will be fixed in
        # https://code.vpac.org/gerrit/#/c/852/
        #
        # self.resetDatastore()
        # software.group = None
        # software.save()
        # self.assertEqual(
        #    self.datastore.method_calls,
        #    [mock.call.save_software(software),
        #     # old accounts are removed
        #     mock.call.remove_account_from_software(account2, software)])
