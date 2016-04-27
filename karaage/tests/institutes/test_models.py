# Copyright 2010, 2013-2015 VPAC
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

from django.core import exceptions as django_exceptions
import mock
import unittest

from karaage.tests.unit import UnitTestCase
from karaage.people.models import Group
from karaage.institutes.models import InstituteQuota
from karaage.tests.fixtures import (InstituteFactory, simple_account,
                                    GroupFactory)


class InstituteTestCase(UnitTestCase):

    def test_add(self):
        InstituteFactory(name='TestInstitute54')

    def test_add_existing_name(self):
        group, _ = Group.objects.get_or_create(name='testinstitute27')
        institute = InstituteFactory(
            name='Test Institute 27', group=group)
        self.assertEqual(
            institute.group.name,
            'testinstitute27')
        self.assertEqual(
            institute.group.name,
            institute.name.lower().replace(' ', ''))

    @unittest.skip("broken with mysql/postgresql")
    def test_username(self):
        assert_raises = self.assertRaises(django_exceptions.ValidationError)

        # Max length
        institution = InstituteFactory(name="a" * 255)
        institution.full_clean()

        # Name is too long
        institution = InstituteFactory(name="a" * 256)
        with assert_raises:
            institution.full_clean()

    def test_change_group(self):
        """Check that when changing an institutes group, old accounts are
        removed from the institute and new ones are added.

        """
        account1 = simple_account(machine_category=self.machine_category)
        group1 = GroupFactory()
        institute = InstituteFactory(group=group1)

        # Test setting up initial group for institute
        self.resetDatastore()
        group1.save()
        group1.add_person(account1.person)
        self.assertEqual(
            self.datastore.method_calls,
            [mock.call.save_group(group1),
             mock.call.add_account_to_group(account1, group1)])

        # Test during initial creation of the institute
        self.resetDatastore()
        institute_quota = InstituteQuota.objects.create(
            machine_category=self.machine_category, institute=institute,
            quota=100)
        self.assertEqual(
            self.datastore.method_calls,
            [mock.call.save_institute(institute),
             mock.call.add_account_to_institute(account1, institute)])

        # Test changing an existing institutions group
        account2 = simple_account(institute=institute,
                                  machine_category=self.machine_category)
        self.resetDatastore()
        group2 = GroupFactory()
        group2.add_person(account2.person)
        institute.group = group2
        institute.save()
        self.assertEqual(
            self.datastore.method_calls,
            [mock.call.save_group(group2),
             mock.call.add_account_to_group(account2, group2),
             mock.call.save_institute(institute),
             # old accounts are removed
             mock.call.remove_account_from_institute(account1, institute),
             # new accounts are added
             mock.call.add_account_to_institute(account2, institute)])

        # Test deleting project quota
        self.resetDatastore()
        institute_quota.delete()
        self.assertEqual(
            self.datastore.method_calls,
            [mock.call.remove_account_from_institute(account2, institute),
             mock.call.delete_institute(institute)])
