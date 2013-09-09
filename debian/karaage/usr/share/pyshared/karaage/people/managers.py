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


class PersonManager(models.Manager):
    def get_query_set(self):
        return super(PersonManager, self).get_query_set().select_related()


class ActivePersonManager(models.Manager):
    def get_query_set(self):
        return super(ActivePersonManager, self).get_query_set().select_related().filter(is_active=True, is_systemuser=False)


class DeletedPersonManager(models.Manager):
    def get_query_set(self):
        return super(DeletedPersonManager, self).get_query_set().filter(is_active=False)


class LeaderManager(models.Manager):
    def get_query_set(self):
        leader_ids = []
        for l in super(LeaderManager, self).get_query_set().filter(is_active=True):
            if l.is_leader():
                leader_ids.append(l.id)

        return self.filter(id__in=leader_ids)
