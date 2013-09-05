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
from django.contrib.auth.models import User
from karaage.util import log_object as log

class PersonManager(models.Manager):
    def get_query_set(self):
        return super(PersonManager, self).get_query_set().select_related()

    def _create_user(self, username, email, password, is_staff, is_superuser, **extra_fields):
        """Creates a new active person. """

        # Create the Django user
        user = User(username=username, email=email,
                is_staff=is_staff, is_active=True,
                is_superuser=is_superuser)
        user.set_password(password)
        user.save()

        #Create Person
        person = self.model(
            user=user,
            **extra_fields
            )
        person.save(self._db)

        log(None, person, 1, 'Created person')
        return person

    def create_user(self, username, email, password=None, **extra_fields):
        """ Creates a new ordinary person. """
        return self._create_user(username=username, email=email,
                password=password, is_staff=False, is_superuser=False,
                **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        """ Creates a new person with super powers. """
        return self._create_user(username=username, email=email,
                password=password, is_staff=True, is_superuser=True,
                **extra_fields)


class ActivePersonManager(PersonManager):
    def get_query_set(self):
        return super(ActivePersonManager, self).get_query_set().select_related().filter(user__is_active=True, is_systemuser=False)


class DeletedPersonManager(PersonManager):
    def get_query_set(self):
        return super(DeletedPersonManager, self).get_query_set().filter(user__is_active=False)


class LeaderManager(PersonManager):
    def get_query_set(self):
        leader_ids = []
        for l in super(LeaderManager, self).get_query_set().filter(user__is_active=True):
            if l.is_leader():
                leader_ids.append(l.id)

        return self.filter(id__in=leader_ids)
