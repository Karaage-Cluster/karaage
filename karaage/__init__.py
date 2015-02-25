# Copyright 2010, 2015 VPAC
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
import os.path
from pkg_resources import get_distribution, DistributionNotFound

# Django 1.7 style AppConfig, see
# http://docs.djangoproject.com/en/1.7/ref/applications/
default_app_config = 'karaage.apps.Karaage'

try:
    _dist = get_distribution('karaage4')
    if not __file__.startswith(os.path.join(_dist.location, 'karaage', '')):
        # not installed, but there is another version that *is*
        raise DistributionNotFound
except DistributionNotFound:
    __version__ = 'development'
else:
    __version__ = _dist.version
