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

import base


class PersonalDataStore(base.PersonalDataStore):
    
    def create_new_user(self, data, hashed_password=None):
        return super(PersonalDataStore, self).create_new_user(data, hashed_password=None)

    def activate_user(self, person):
        person = super(PersonalDataStore, self).activate_user(person)
        person.save()
        return person

    def delete_user(self, person):
        super(PersonalDataStore, self).delete_user(person)
        
    def update_user(self, person):
        super(PersonalDataStore, self).update_user(person)

    def is_locked(self, person):
        super(PersonalDataStore, self).is_locked(person)

    def lock_user(self, person):
        super(PersonalDataStore, self).lock_user(person)

    def unlock_user(self, person):
        super(PersonalDataStore, self).unlock_user(person)

    def set_password(self, person, raw_password):
        super(PersonalDataStore, self).set_password(person, raw_password)

    def user_exists(self, username):
        super(PersonalDataStore, self).user_exists(username)


class AccountDataStore(base.AccountDataStore):

    def create_account(self, person, default_project):
        return super(AccountDataStore, self).create_account(person, default_project)

    def delete_account(self, ua):
        super(AccountDataStore, self).delete_account(ua)

    def update_account(self, ua):
        super(AccountDataStore, self).update_account(ua)
  
    def lock_account(self, ua):
        super(AccountDataStore, self).lock_account(ua)

    def unlock_account(self, ua):
        super(AccountDataStore, self).unlock_account(ua)
