# Copyright 2007-2010 VPAC
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
import datetime

class MachineCategoryManager(models.Manager):
    def get_default(self):
        from django.conf import settings
        return self.get(pk=settings.DEFAULT_MC)


class ActiveMachineManager(models.Manager):
    def get_query_set(self):
        today = datetime.datetime.today()
        return super(ActiveMachineManager, self).get_query_set().filter(end_date__isnull=True)
