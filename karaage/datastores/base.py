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

    def save_user(self, person):
        pass

    def delete_user(self, person):
        pass

    def lock_user(self, person):
        pass

    def unlock_user(self, person):
        pass

    def set_password(self, person, raw_password):
        pass

    def user_exists(self, username):
        return False

    def change_username(self, person, new_username):
        pass

    def get_user_details(self, person):
        return { }

class AccountDataStore(object):

    def save_account(self, ua):
        pass

    def delete_account(self, ua):
        pass

    def lock_account(self, ua):
        self.change_shell(ua, settings.LOCKED_SHELL)

    def unlock_account(self, ua):
        self.change_shell(ua, ua.shell)

    def change_shell(self, ua, shell):
        pass

    def account_exists(self, username):
        return False

    def set_password(self, ua, raw_password):
        pass

    def change_username(self, ua, new_username):
        pass

    def get_account_details(self, ua):
        return {}

    def add_group(self, ua, group):
        pass

    def remove_group(self, ua, group):
        pass

    def save_group(self, group):
        pass

    def delete_group(self, group):
        pass

    def get_group_details(self, group):
        return {}

