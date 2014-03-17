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

from django.test import TestCase

from karaage.people.forms import AddPersonForm
from karaage.tests.fixtures import ProjectFactory


class AddPersonFormTestCase(TestCase):
    def _valid_user(self):
        project = ProjectFactory()
        valid_user = {
            'username': 'testuser',
            'project': project.id,
            'institute': project.institute.id,
            'full_name': 'Joe Blow',
            'short_name': 'Joe',
            'needs_account': True,
            'email': 'test@example.com',
            'telephone': '8888888888',
            'password1': 'wai5bixa8Igohxa',
            'password2': 'wai5bixa8Igohxa'}
        return valid_user

    def test_valid_data(self):
        form_data = self._valid_user()
        form = AddPersonForm(data=form_data)
        self.assertEqual(form.is_valid(), True, form.errors.items())

    def test_invalid_username(self):
        form_data = self._valid_user()
        form_data['username'] = '!invalid!'
        form = AddPersonForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors.items(),
            [('username',
              [u'Usernames can only contain '
               u'letters, numbers and underscores'])])

    def test_upper_username(self):
        form_data = self._valid_user()
        form_data['username'] = 'INVALID'
        form = AddPersonForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors.items(),
            [('username',
              [u'Username must be all lowercase'])])

    def test_long_username(self):
        form_data = self._valid_user()
        form_data['username'] = 'long' * 100
        form = AddPersonForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors.items(),
            [('username',
              [u'Ensure this value has at most '
               u'255 characters (it has 400).'])])
