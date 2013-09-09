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

from karaage.util import log_object as log
from django.contrib.auth.models import BaseUserManager

class PersonManager(BaseUserManager):
    def get_query_set(self):
        return super(PersonManager, self).get_query_set().select_related()

    def _create_user(self, username, email, short_name, full_name,
            institute, password, is_admin, **extra_fields):
        """Creates a new active person. """

        #Create Person
        person = self.model(
            username=username, email=email,
            short_name=short_name, full_name=full_name,
            is_admin=is_admin, is_active=True,
            institute=institute,
            **extra_fields
            )
        person.set_password(password)
        person.save(self._db)

        log(None, person, 1, 'Created person')
        return person

    def create_user(self, username, email, short_name, full_name,
            institute, password=None, **extra_fields):
        """ Creates a new ordinary person. """
        return self._create_user(username=username, email=email,
                short_name=short_name, full_name=full_name,
                institute=institute, password=password,
                is_admin=False, **extra_fields)

    def create_superuser(self, username, email, short_name, full_name,
            institute, password, **extra_fields):
        """ Creates a new person with super powers. """
        return self._create_user(username=username, email=email,
                institute=institute, password=password,
                short_name=short_name, full_name=full_name,
                is_admin=True, **extra_fields)


class ActivePersonManager(PersonManager):
    def get_query_set(self):
        return super(ActivePersonManager, self).get_query_set().select_related().filter(is_active=True, is_systemuser=False)


class DeletedPersonManager(PersonManager):
    def get_query_set(self):
        return super(DeletedPersonManager, self).get_query_set().filter(is_active=False)


class LeaderManager(PersonManager):
    def get_query_set(self):
        leader_ids = []
        for l in super(LeaderManager, self).get_query_set().filter(is_active=True):
            if l.is_leader():
                leader_ids.append(l.id)

        return self.filter(id__in=leader_ids)
