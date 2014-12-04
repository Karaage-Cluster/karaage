# -*- coding: utf-8 -*-
#
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
import os.path
SYSTEM_SETTINGS_PATH = "/etc/karaage3/settings.py"

from .defaults import *  # NOQA

if os.path.isfile(SYSTEM_SETTINGS_PATH):
    exec(open(SYSTEM_SETTINGS_PATH, "rb").read())

import sys
from .process import post_process
post_process(sys.modules[__name__])
