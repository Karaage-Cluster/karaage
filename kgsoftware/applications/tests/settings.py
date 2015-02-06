# Copyright 2007-2014 VPAC
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

from karaage.conf.defaults import *  # NOQA
from karaage.tests.defaults import *  # NOQA

PLUGINS = [
    'kgsoftware.plugin',
    'kgsoftware.applications.plugin',
]
DEBUG = False
ALLOWED_HOSTS = ["localhost"]

import sys
from karaage.conf.process import post_process
post_process(sys.modules[__name__])
