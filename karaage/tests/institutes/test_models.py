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

from django.core import exceptions as django_exceptions
from django.test import TestCase

from karaage.people.models import Group
from karaage.institutes.models import Institute
from karaage.tests.fixtures import InstituteFactory


class InstituteTestCase(TestCase):

    def test_add(self):
        institute = Institute.objects.create(name='TestInstitute54')
        self.assertEqual(
            institute.group.name,
            'testinstitute54')
        self.assertEqual(
            institute.group.name,
            institute.name.lower().replace(' ', ''))

    def test_add_spaces(self):
        institute = Institute.objects.create(name='Test Institute 60')
        self.assertEqual(
            institute.group.name,
            'testinstitute60')
        self.assertEqual(
            institute.group.name,
            institute.name.lower().replace(' ', ''))

    def test_add_existing_name(self):
        Group.objects.get_or_create(name='testinstitute27')
        institute = Institute.objects.create(name='Test Institute 27')
        self.assertEqual(
            institute.group.name,
            'testinstitute27')
        self.assertEqual(
            institute.group.name,
            institute.name.lower().replace(' ', ''))

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
        group, _ = Group.objects.get_or_create(name='example')
        institute = Institute.objects.create(name='test')
        institute.group = group
        institute.save()
