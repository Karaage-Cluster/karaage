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

from karaage.datastores import base
from karaage.datastores import ldap_schemas

from django.conf import settings

def str_or_none(string):
    if string is None or string == "":
        return None
    return string

class PersonalDataStore(base.PersonalDataStore):
    pass


class AccountDataStore(base.AccountDataStore):

    def create_account(self, ua):
        super(AccountDataStore, self).create_account(ua)

        person = ua.user

        luser = ldap_schemas.account()
        luser.set_defaults()
        luser.uid = person.username
        luser.givenName = person.first_name
        luser.sn = person.last_name
        luser.telephoneNumber = str_or_none(person.telephone)
        luser.mail = str_or_none(person.email)
        luser.title = str_or_none(person.title)
        luser.o = person.institute.name
        luser.userPassword = "" # FIXME

        luser.gidNumber = person.institute.gid
        luser.homeDirectory = settings.HOME_DIRECTORY % { 'default_project': ua.default_project.pid, 'uid': luser.uid }
        luser.loginShell = ua.shell
        luser.pre_create(master=None)
        luser.pre_save()
        luser.save()

    def delete_account(self, ua):
        super(AccountDataStore, self).delete_account(ua)
        luser = ldap_schemas.account.objects.get(uid=ua.username)
        luser.pre_delete()
        luser.delete()

    def update_account(self, ua):
        super(AccountDataStore, self).update_account(ua)

        person = ua.user

        luser = ldap_schemas.account.objects.get(uid=ua.username)
        luser.gidNumber = ua.user.institute.gid
        luser.givenName = person.first_name
        luser.sn = person.last_name
        luser.telephoneNumber = str_or_none(person.telephone)
        luser.mail = str_or_none(person.email)
        luser.title = str_or_none(person.title)
        luser.o = person.institute.name
        luser.pre_save()
        luser.save()

    def lock_account(self, ua):
        super(AccountDataStore, self).lock_account(ua)

    def unlock_account(self, ua):
        super(AccountDataStore, self).unlock_account(ua)

    def change_shell(self, ua, shell):
        super(AccountDataStore, self).change_shell(ua, shell)
        luser = ldap_schemas.account.objects.get(uid=ua.username)
        luser.loginShell = shell
        luser.pre_save()
        luser.save()

    def set_password(self, ua, raw_password):
        super(AccountDataStore, self).set_password(ua, raw_password)
        p = ldap_schemas.account.objects.get(uid=ua.username)
        p.change_password(raw_password)
        p.pre_save()
        p.save()

    def account_exists(self, username):
        try:
            ldap_schemas.account.objects.get(uid=username)
            return True
        except ldap_schemas.account.DoesNotExist:
            return False

    def change_username(self, ua, new_username):
        super(AccountDataStore, self).change_username(ua, new_username)
        p = ldap_schemas.account.objects.get(uid=ua.username)
        p.rename(uid=new_username)
