# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
#
# This file is part of Karaage.
#
# Karaage is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Karaage is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Karaage If not, see <http://www.gnu.org/licenses/>.

try:
    from mock import Mock
except ImportError:
    raise ImportError(
        "mock is required, "
        "either install from a package or using \'pip install -e .[tests]\'")
from django.test import TestCase

from karaage.datastores import _DATASTORES
from karaage.middleware.threadlocals import reset


class UnitTestCase(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        self.resetDatastore()

        def cleanup():
            _DATASTORES.clear()
            reset()
        self.addCleanup(cleanup)

    def resetDatastore(self):
        self.datastore = Mock()
        _DATASTORES.clear()
        _DATASTORES.append(self.datastore)
