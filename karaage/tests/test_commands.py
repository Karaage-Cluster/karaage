# Copyright 2014-2015 VPAC
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
from django.core.management import call_command

from mock import Mock

from karaage.signals import daily_cleanup


class CommandsTestCase(TestCase):

    def test_daily_cleanup(self):
        callback = Mock()
        daily_cleanup.connect(callback)

        try:
            call_command('daily_cleanup')
        finally:
            daily_cleanup.disconnect(daily_cleanup)

        self.assertEqual(callback.call_count, 1)
