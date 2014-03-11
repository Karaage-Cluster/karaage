# Copyright 2007-2014 VPAC
# Copyright 2014 University of Melbourne
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

import logging


LOG = logging.getLogger(__name__)


def assert_password_simple(password, old=None):
    if old and password == old:
        raise ValueError('Old and new passwords are the same.')
    elif len(password) < 6:
        raise ValueError('Password is less than six characters.')
    return password


try:
    from crack import VeryFascistCheck as _assert_password
    _assert_password('thaeliez4niore0U')
except ImportError:
    _assert_password = assert_password_simple
except (OSError, ValueError), e:
    LOG.warning("Cracklib misconfigured: %s", str(e))
    _assert_password = assert_password_simple


def assert_strong_password(password, old_password=None):
    """Return the password is valid. Otherwise raise ValueError."""
    return _assert_password(password, old_password)
