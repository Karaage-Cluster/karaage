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

from django.test import TestCase
from django import forms as django_forms

from karaage.common import forms


class FormsTestCase(TestCase):

    def test_validate_password(self):
        username = "somebody"

        good_password = 'ephiikee0eef2Gae'
        bad_password = 'test'
        old_password = 'JaicaeyaivahD9ph'

        # Long enough.
        res = forms.validate_password(username, good_password)
        self.assertEqual(res, good_password)

        # Passwords match.
        res = forms.validate_password(
            username, good_password, good_password)
        self.assertEqual(res, good_password)

        # New password is different to old password.
        res = forms.validate_password(
            username, good_password, old_password=old_password)
        self.assertEqual(res, good_password)

        # New password is different to old password, passwords match.
        res = forms.validate_password(
            username, good_password, good_password, old_password=old_password)
        self.assertEqual(res, good_password)

        assert_raises = self.assertRaises(django_forms.ValidationError)

        # Too short.
        with assert_raises:
            forms.validate_password(username, bad_password)

        # password contains username
        with assert_raises:
            forms.validate_password(
                username, "2222" + username + "1111")

        # Passwords don't match.
        with assert_raises:
            forms.validate_password(
                username, good_password, good_password + 'diff')

        # New password is the same as old password.
        with assert_raises:
            forms.validate_password(
                username, good_password, old_password=good_password)

        # Second password isn't blank.
        with assert_raises:
            forms.validate_password(
                username, good_password, '')
