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

from karaage.tests.fixtures import AccountFactory


@pytest.mark.django_db
class AccountTestCase(TestCase):
    @unittest.skip("broken with mysql/postgresql")
    def test_username(self):
        assert_raises = self.assertRaises(django_exceptions.ValidationError)

        # Max length
        account = AccountFactory(username="a" * 255)
        account.full_clean()

        # Name is too long
        account = AccountFactory(username="a" * 256)
        with assert_raises:
            account.full_clean()
