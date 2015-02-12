# Copyright 2015 VPAC
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

from django.test import TestCase

from karaage.tests.fixtures import GroupFactory, simple_account

from .fixtures import SoftwareFactory


class SoftwareTestCase(TestCase):

    def test_change_group(self):
        """Check that when changing an software group, old accounts are
        removed from the software and new ones are added.

        """
        account1 = simple_account()
        group1 = GroupFactory()
        group1.add_person(account1.person)

        # Test during initial creation of the software
        software = SoftwareFactory(group=group1)

        # Test changing an existing software group
        account2 = simple_account()
        group2 = GroupFactory()
        group2.add_person(account2.person)
        software.group = group2
        software.save()
