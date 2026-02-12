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

from __future__ import absolute_import

import logging

from django.conf import settings

LOG = logging.getLogger(__name__)


try:
    from cracklib import VeryFascistCheck as _assert_password

    # Some configuration errors are only apparent when cracklib
    # tests a password for the first time, so test a strong password to
    # verify that cracklib is working as intended.
    _assert_password("thaeliez4niore0U")
except ImportError as e:
    LOG.error("Cracklib misconfigured: %s", str(e))
    raise e
except (OSError, ValueError) as e:
    LOG.error("Cracklib misconfigured: %s", str(e))
    raise ImportError("Cracklib misconfigured: %s" % str(e))


def assert_strong_password(username, password, old_password=None):
    """Raises ValueError if the password isn't strong.

    Returns the password otherwise."""

    # test the length
    try:
        minlength = settings.MIN_PASSWORD_LENGTH
    except AttributeError:
        minlength = 12
    if len(password) < minlength:
        raise ValueError("Password must be at least %s characters long" % minlength)

    if username is not None and username in password:
        raise ValueError("Password contains username")

    return _assert_password(password, old_password)
