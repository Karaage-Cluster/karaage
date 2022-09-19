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

import pytest
from django.core import exceptions as django_exceptions
from django.test import TestCase

from karaage.people.models import Group, Person
from karaage.tests.fixtures import InstituteFactory, PersonFactory


@pytest.mark.django_db
class PersonTestCase(TestCase):
    def test_minimum_create(self):
        institute = InstituteFactory()
        person = Person.objects.create(
            username="mchagr",
            password="test",
            short_name="RK",
            full_name="Rick Spicy McHaggis",
            email="test@example.com",
            institute=institute,
        )
        person.full_clean()
        self.assertFalse(person.is_admin)
        self.assertFalse(person.is_systemuser)
        self.assertEqual(str(person), "Rick Spicy McHaggis")
        self.assertEqual(person.short_name, "RK")
        self.assertEqual(person.email, "test@example.com")
        self.assertEqual(person.first_name, "Rick Spicy")
        self.assertEqual(person.last_name, "McHaggis")

    @unittest.skip("broken with mysql/postgresql")
    def test_username(self):
        assert_raises = self.assertRaises(django_exceptions.ValidationError)

        # Max length
        person = PersonFactory(username="a" * 255)
        person.full_clean()

        # Name is too long
        person = PersonFactory(username="a" * 256)
        with assert_raises:
            person.full_clean()

    def test_locking(self):
        person = PersonFactory()
        self.assertTrue(person.login_enabled)

        # Test that a locked person is disabled
        person.lock()
        self.assertFalse(person.login_enabled)

        # Test that an unlocked person is enabled
        person.unlock()
        self.assertTrue(person.login_enabled)


@pytest.mark.django_db
class GroupTestCase(TestCase):
    def test_minimum_create(self):
        group = Group.objects.create(foreign_id="1111", name="test_group")
        group.full_clean()
