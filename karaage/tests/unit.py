# Copyright 2014-2015 VPAC
# Copyright 2014 The University of Melbourne
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

from karaage.middleware.threadlocals import reset
from karaage.datastores import _MACHINE_CATEGORY_DATASTORES
from karaage.tests.fixtures import MachineCategoryFactory


class UnitTestCase(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        self.resetDatastore()
        self.machine_category = MachineCategoryFactory(datastore='mock')

        def cleanup():
            _MACHINE_CATEGORY_DATASTORES['mock'] = []
            reset()
        self.addCleanup(cleanup)

    def resetDatastore(self):
        self.datastore = Mock()
        _MACHINE_CATEGORY_DATASTORES['mock'] = [self.datastore]
