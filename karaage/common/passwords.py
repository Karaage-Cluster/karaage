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

from __future__ import absolute_import
import logging


LOG = logging.getLogger(__name__)


def assert_password_simple(password, old=None):
    if old and password == old:
        raise ValueError('Old and new passwords are the same.')
    elif len(password) < 6:
        raise ValueError('Password is less than six characters.')
    return password


try:
    from cracklib import VeryFascistCheck as _assert_password
    # Some configuration errors are only apparent when cracklib
    # tests a password for the first time, so test a strong password to
    # verify that cracklib is working as intended.
    _assert_password('thaeliez4niore0U')
except ImportError:
    _assert_password = assert_password_simple
except (OSError, ValueError) as e:
    LOG.warning("Cracklib misconfigured: %s", str(e))
    _assert_password = assert_password_simple


def assert_strong_password(username, password, old_password=None):
    """Raises ValueError if the password isn't strong.

    Returns the password otherwise."""
    if username is not None and username in password:
        raise ValueError("Password contains username")

    return _assert_password(password, old_password)
