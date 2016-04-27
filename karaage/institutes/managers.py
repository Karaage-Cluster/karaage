# Copyright 2008, 2010, 2014-2015 VPAC
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

from django.db import models


class ActiveInstituteManager(models.Manager):
    """
    Returns only 'active' institutes.
    """

    def get_queryset(self):
        query = super(ActiveInstituteManager, self).get_queryset()
        return query.filter(is_active=True)
