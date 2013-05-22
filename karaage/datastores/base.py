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
        return None

    def change_username(self, person, new_username):
        pass


class AccountDataStore(object):

    def create_account(self, ua, person):
        pass

    def delete_account(self, ua):
        pass

    def update_account(self, ua):
        pass

    def lock_account(self, ua):
        self.change_shell(ua, settings.LOCKED_SHELL)

    def unlock_account(self, ua):
        self.change_shell(ua, ua.shell)

    def change_shell(self, ua, shell):
        pass
