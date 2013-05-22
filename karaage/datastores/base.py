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

from django.contrib.auth.models import User
from django.conf import settings

import datetime
from andsome.middleware.threadlocals import get_current_user

from karaage.people.models import Person
from karaage.machines.models import UserAccount
from karaage.util import log_object as log


class PersonalDataStore(object):

    def activate_user(self, person):
        pass

    def delete_user(self, person):
        pass

    def update_user(self, person):
        pass

    def lock_user(self, person):
        pass

    def unlock_user(self, person):
        pass

    def set_password(self, person, raw_password):
        pass

    def user_exists(self, username):
        pass

    def create_password_hash(self, raw_password):
        pass

    def change_username(self, person, new_username):
        pass


class AccountDataStore(object):

    def __init__(self, machine_category):
        self.machine_category = machine_category
    
    def create_account(self, person, default_project):
        """Creates a UserAccount (if needed) and activates user.

        Keyword arguments:
        person_id -- Person id
        project_id -- Project id
        
        """
        ua = UserAccount.objects.create(
            user=person, username=person.username,
            shell=settings.DEFAULT_SHELL,
            machine_category=self.machine_category,
            default_project=default_project,
            date_created=datetime.datetime.today())
    
        if default_project is not None:
            from karaage.projects.utils import add_user_to_project
            add_user_to_project(person, default_project)
    
        log(get_current_user(), ua.user, 1, 'Created account on %s' % self.machine_category)

        return ua

    def delete_account(self, ua):
        if not ua.date_deleted:
            ua.date_deleted = datetime.datetime.now()
            ua.save()
        from karaage.projects.utils import remove_user_from_project
        for project in ua.project_list():
            
            remove_user_from_project(ua.user, project)
        log(get_current_user(), ua.user, 3, 'Deleted account on %s' % ua.machine_category)
        
    def update_account(self, ua):
        pass

    def lock_account(self, ua):
        from karaage.datastores import change_shell
        change_shell(ua, settings.LOCKED_SHELL)

    def unlock_account(self, ua):
        from karaage.datastores import change_shell
        change_shell(ua, ua.shell)

    def change_shell(self, ua, shell):
        pass
