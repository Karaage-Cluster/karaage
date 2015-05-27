# Copyright 2008, 2010-2011, 2013-2015 VPAC
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

from django.contrib.auth.models import BaseUserManager
from django.contrib.auth import authenticate


class PersonManager(BaseUserManager):

    def authenticate(self, username, password):
        return authenticate(username=username, password=password)

    def get_queryset(self):
        return super(PersonManager, self).get_queryset().select_related()

    def _create_user(
            self, username, email, short_name, full_name,
            institute, password, is_admin, **extra_fields):
        """Creates a new active person. """

        # Create Person
        person = self.model(
            username=username, email=email,
            short_name=short_name, full_name=full_name,
            is_admin=is_admin,
            institute=institute,
            **extra_fields
        )
        person.set_password(password)
        person.save()
        return person

    def create_user(
            self, username, email, short_name, full_name,
            institute, password=None, **extra_fields):
        """ Creates a new ordinary person. """
        return self._create_user(
            username=username, email=email,
            short_name=short_name, full_name=full_name,
            institute=institute, password=password,
            is_admin=False, **extra_fields)

    def create_superuser(
            self, username, email, short_name, full_name,
            institute, password, **extra_fields):
        """ Creates a new person with super powers. """
        return self._create_user(
            username=username, email=email,
            institute=institute, password=password,
            short_name=short_name, full_name=full_name,
            is_admin=True, **extra_fields)


class ActivePersonManager(PersonManager):

    def get_queryset(self):
        return super(ActivePersonManager, self) \
            .get_queryset() \
            .select_related() \
            .filter(is_active=True, is_systemuser=False)


class DeletedPersonManager(PersonManager):

    def get_queryset(self):
        return super(DeletedPersonManager, self) \
            .get_queryset() \
            .filter(is_active=False)


class LeaderManager(PersonManager):

    def get_queryset(self):
        leader_ids = []
        query = super(LeaderManager, self).get_queryset()
        query = query.filter(is_active=True)
        for l in query:
            if l.is_leader():
                leader_ids.append(l.id)

        return self.filter(id__in=leader_ids)
