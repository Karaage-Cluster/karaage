# Copyright 2007-2013 VPAC
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

import re

from django.conf import settings

from karaage.people.models import Person
from karaage.datastores import person_exists, account_exists
from karaage.machines.models import MachineCategory

username_re = re.compile(r'^[-\w]+$')

class UsernameException(Exception):
    pass


class UsernameInvalid(UsernameException):
    pass


class UsernameTaken(UsernameException):
    pass
    
    
def validate_username(username):
    
        if username:
            if not username.islower():
                raise UsernameInvalid(u'Username must be all lowercase')
            if len(username) < 2:
                raise UsernameInvalid(u'Username must be at least 2 characters')
            if not username_re.search(username):
                raise UsernameInvalid(u'Usernames can only contain letters, numbers and underscores')

            try:
                user = Person.objects.get(user__username__exact=username)
            except Person.DoesNotExist:
                user = None

            if user is not None:
                raise UsernameTaken(u'The username is already taken. Please choose another. If this was the name of your old account please email %s' % settings.ACCOUNTS_EMAIL)

            if person_exists(username):
                raise UsernameTaken(u'Username is already in external personal datastore.')

            for mc in MachineCategory.objects.all():
                if account_exists(username, mc):
                     raise UsernameTaken(u'Username is already in external account datastore.')

        return username
