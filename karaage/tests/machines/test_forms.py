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
from django.conf import settings

from karaage.machines.forms import AdminAccountForm
from karaage.tests.fixtures import simple_account


class AdminAccountFormTestCase(TestCase):

    def setUp(self):
        super(AdminAccountFormTestCase, self).setUp()
        self.account = simple_account()

    def _valid_form_data(self):
        text = six.text_type
        data = {
            'username': self.account.username,
            'machine_category': text(self.account.machine_category.id),
            'default_project': text(self.account.default_project.id),
            'shell': settings.DEFAULT_SHELL,
        }
        return data

    def test_valid_data(self):
        form_data = self._valid_form_data()
        form_data['username'] = 'test-account'
        form = AdminAccountForm(person=self.account.person,
                                data=form_data,
                                instance=self.account)
        self.assertEqual(form.is_valid(), True, form.errors.items())
        form.save()
        self.assertEqual(self.account.username, 'test-account')

    def test_invalid_usernamen(self):
        form_data = self._valid_form_data()
        form_data['username'] = '!test-account'
        form = AdminAccountForm(person=self.account.person,
                                data=form_data,
                                instance=self.account)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors.items(),
            dict.items({
                'username': [(six.u(
                    'Usernames can only contain '
                    'letters, numbers and underscores'))]
            })
        )

    def test_upper_username(self):
        form_data = self._valid_form_data()
        form_data['username'] = 'INVALID'
        form = AdminAccountForm(person=self.account.person,
                                data=form_data,
                                instance=self.account)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors.items(),
            dict.items({
                'username': [six.u('Username must be all lowercase')]
            })
        )

    def test_long_username(self):
        form_data = self._valid_form_data()
        form_data['username'] = 'long' * 100
        form = AdminAccountForm(person=self.account.person,
                                data=form_data,
                                instance=self.account)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors.items(),
            dict.items({
                'username': [six.u(
                    'Ensure this value has at '
                    'most 255 characters (it has 400).')]
            })
        )
