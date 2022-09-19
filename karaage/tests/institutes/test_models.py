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

import unittest

import mock
import pytest
from django.core import exceptions as django_exceptions

from karaage.people.models import Group
from karaage.tests.fixtures import (
    GroupFactory,
    InstituteFactory,
    simple_account,
)
from karaage.tests.unit import UnitTestCase


@pytest.mark.django_db
class InstituteTestCase(UnitTestCase):
    def test_add(self):
        InstituteFactory(name="TestInstitute54")

    def test_add_existing_name(self):
        group, _ = Group.objects.get_or_create(name="testinstitute27")
        institute = InstituteFactory(name="Test Institute 27", group=group)
        self.assertEqual(institute.group.name, "testinstitute27")
        self.assertEqual(institute.group.name, institute.name.lower().replace(" ", ""))

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
        account1 = simple_account()
        group1 = GroupFactory()

        # Test initial creation of the institute
        self.resetDatastore()
        institute = InstituteFactory(group=group1)
        self.assertEqual(self.datastore.method_calls, [mock.call.save_institute(institute)])

        # Test setting up initial group for institute
        self.resetDatastore()
        group1.save()
        group1.add_person(account1.person)
        self.assertEqual(
            self.datastore.method_calls,
            [
                mock.call.save_group(group1),
                mock.call.add_account_to_group(account1, group1),
                mock.call.add_account_to_institute(account1, institute),
            ],
        )

        # Test changing an existing institutions group
        account2 = simple_account(institute=institute)
        self.resetDatastore()
        group2 = GroupFactory()
        group2.add_person(account2.person)
        group2.save()
        institute.group = group2
        institute.save()
        self.assertEqual(
            self.datastore.method_calls,
            [
                mock.call.save_group(group2),
                mock.call.add_account_to_group(account2, group2),
                mock.call.save_group(group2),
                mock.call.save_institute(institute),
                # old accounts are removed
                mock.call.remove_account_from_institute(account1, institute),
                # new accounts are added
                mock.call.add_account_to_institute(account2, institute),
            ],
        )

        # Test deleting institute
        self.resetDatastore()
        institute.delete()
        self.assertEqual(
            self.datastore.method_calls,
            [mock.call.remove_account_from_institute(account2, institute), mock.call.delete_institute(institute)],
        )
