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

from django.test import TestCase

import karaage.people.forms as forms
import karaage.tests.fixtures as fixtures
from karaage.tests.integration import skip_if_missing_requirements


class AddPersonFormTestCase(TestCase):

    def _valid_user(self):
        project = fixtures.ProjectFactory()
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
        form = forms.AddPersonForm(data=form_data)
        self.assertEqual(form.is_valid(), True, form.errors.items())
        self.assertEqual(form.cleaned_data['password1'], 'wai5bixa8Igohxa')
        self.assertEqual(form.cleaned_data['password2'], 'wai5bixa8Igohxa')

    @skip_if_missing_requirements('cracklib')
    def test_password_short(self):
        form_data = self._valid_user()
        form_data['password1'] = 'abc'
        form_data['password2'] = 'abc'
        form = forms.AddPersonForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors.items(),
            dict.items({
                'password2': [six.u(
                    'Your password was found to be insecure: '
                    'it is WAY too short. '
                    'A good password has a combination of '
                    'letters (uppercase, lowercase), numbers '
                    'and is at least 8 characters long.')]
            })
        )

    @skip_if_missing_requirements('cracklib')
    def test_password_simple(self):
        form_data = self._valid_user()
        form_data['password1'] = 'qwerty'
        form_data['password2'] = 'qwerty'
        form = forms.AddPersonForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors.items(),
            dict.items({
                'password2': [six.u(
                    'Your password was found to be insecure: '
                    'it is based on a dictionary word. '
                    'A good password has a combination of '
                    'letters (uppercase, lowercase), numbers '
                    'and is at least 8 characters long.')]
            })
        )

    def test_password_mismatch(self):
        form_data = self._valid_user()
        form_data['password2'] = '!invalid!'
        form = forms.AddPersonForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors.items(),
            dict.items({
                'password2': [six.u('The two password fields didn\'t match.')]
            })
        )

    def test_invalid_username(self):
        form_data = self._valid_user()
        form_data['username'] = '!invalid!'
        form = forms.AddPersonForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors.items(),
            dict.items({
                'username': [six.u(
                    'Usernames can only contain '
                    'letters, numbers and underscores')]
            })
        )

    def test_upper_username(self):
        form_data = self._valid_user()
        form_data['username'] = 'INVALID'
        form = forms.AddPersonForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors.items(),
            dict.items({
                'username': [six.u('Username must be all lowercase')]
            })
        )

    def test_long_username(self):
        form_data = self._valid_user()
        form_data['username'] = 'long' * 100
        form = forms.AddPersonForm(data=form_data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors.items(),
            dict.items({
                'username': [six.u(
                    'Ensure this value has at most '
                    '255 characters (it has 400).')]
            })
        )


class AdminPasswordChangeFormTestCase(TestCase):

    def _valid_change(self):
        person = fixtures.PersonFactory()

        valid_change = {
            'username': person.username,
            'new1': 'wai5bixa8Igohxa',
            'new2': 'wai5bixa8Igohxa'}
        return person, valid_change

    def test_valid_data(self):
        person, form_data = self._valid_change()
        form = forms.AdminPasswordChangeForm(data=form_data, person=person)
        self.assertEqual(form.is_valid(), True, form.errors.items())
        self.assertEqual(form.cleaned_data['new1'], 'wai5bixa8Igohxa')
        self.assertEqual(form.cleaned_data['new2'], 'wai5bixa8Igohxa')

    @skip_if_missing_requirements('cracklib')
    def test_password_short(self):
        person, form_data = self._valid_change()
        form_data['new1'] = 'abc'
        form_data['new2'] = 'abc'
        form = forms.AdminPasswordChangeForm(data=form_data, person=person)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors.items(),
            dict.items({
                'new2': [six.u(
                    'Your password was found to be insecure: '
                    'it is WAY too short. '
                    'A good password has a combination of '
                    'letters (uppercase, lowercase), numbers '
                    'and is at least 8 characters long.')]
            })
        )

    @skip_if_missing_requirements('cracklib')
    def test_password_simple(self):
        person, form_data = self._valid_change()
        form_data['new1'] = 'qwerty'
        form_data['new2'] = 'qwerty'
        form = forms.AdminPasswordChangeForm(data=form_data, person=person)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors.items(),
            dict.items({
                'new2': [six.u(
                    'Your password was found to be insecure: '
                    'it is based on a dictionary word. '
                    'A good password has a combination of '
                    'letters (uppercase, lowercase), numbers '
                    'and is at least 8 characters long.')]
            })
        )

    def test_password_mismatch(self):
        person, form_data = self._valid_change()
        form_data['new2'] = '!invalid!'
        form = forms.AdminPasswordChangeForm(data=form_data, person=person)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors.items(),
            dict.items({
                'new2': [six.u('The two password fields didn\'t match.')]
            })
        )


class PasswordChangeFormTestCase(TestCase):

    def _valid_change(self):
        person = fixtures.PersonFactory()

        valid_change = {
            'username': person.username,
            'old': 'test',
            'new1': 'wai5bixa8Igohxa',
            'new2': 'wai5bixa8Igohxa'}
        return person, valid_change

    def test_valid_data(self):
        person, form_data = self._valid_change()
        form = forms.PasswordChangeForm(data=form_data, person=person)
        self.assertEqual(form.is_valid(), True, form.errors.items())
        self.assertEqual(form.cleaned_data['new1'], 'wai5bixa8Igohxa')
        self.assertEqual(form.cleaned_data['new2'], 'wai5bixa8Igohxa')

    def test_password_old_password_wrong(self):
        person, form_data = self._valid_change()
        form_data['old'] = 'abc'
        form = forms.PasswordChangeForm(data=form_data, person=person)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors.items(),
            dict.items({
                'old': [six.u('Your old password was incorrect')]
            })
        )

    @skip_if_missing_requirements('cracklib')
    def test_password_short(self):
        person, form_data = self._valid_change()
        form_data['new1'] = 'abc'
        form_data['new2'] = 'abc'
        form = forms.PasswordChangeForm(data=form_data, person=person)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors.items(),
            dict.items({
                'new2': [six.u(
                    'Your password was found to be insecure: '
                    'it is WAY too short. '
                    'A good password has a combination of '
                    'letters (uppercase, lowercase), numbers '
                    'and is at least 8 characters long.')]
            })
        )

    @skip_if_missing_requirements('cracklib')
    def test_password_simple(self):
        person, form_data = self._valid_change()
        form_data['new1'] = 'qwerty'
        form_data['new2'] = 'qwerty'
        form = forms.PasswordChangeForm(data=form_data, person=person)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors.items(),
            dict.items({
                'new2': [six.u(
                    'Your password was found to be insecure: '
                    'it is based on a dictionary word. '
                    'A good password has a combination of '
                    'letters (uppercase, lowercase), numbers '
                    'and is at least 8 characters long.')]
            })
        )

    def test_password_mismatch(self):
        person, form_data = self._valid_change()
        form_data['new2'] = '!invalid!'
        form = forms.PasswordChangeForm(data=form_data, person=person)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors.items(),
            dict.items({
                'new2': [six.u('The two password fields didn\'t match.')]
            })
        )
