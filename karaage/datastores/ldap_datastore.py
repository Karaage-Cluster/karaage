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
    
    def create_new_user(self, data, hashed_password):
        return super(PersonalDataStore, self).create_new_user(data, hashed_password)

    def activate_user(self, person):
        person = super(PersonalDataStore, self).activate_user(person)

        p = ldap_schemas.person()
        p.set_defaults()
        p.uid = person.username
        p.givenName = person.first_name
        p.sn = person.last_name
        p.telephoneNumber = str_or_none(person.telephone)
        p.mail = str_or_none(person.email)
        p.title = str_or_none(person.title)
        p.o = person.institute.name
        p.userPassword = str(person.user.password)
        p.pre_create(master=None)
        p.pre_save()
        p.save()

        # super.activate_user(person) sets user.password to LDAP password that
        # django doesn't understand. Need to reset it.
        person.user.set_unusable_password()
        person.user.save()

        return person

    def delete_user(self, person):
        super(PersonalDataStore, self).delete_user(person)
        try:
            p = ldap_schemas.person.objects.get(uid=person.username)
            p.pre_delete()
            p.delete()
        except ldap_schemas.person.DoesNotExist:
            pass

    def update_user(self, person):
        super(PersonalDataStore, self).update_user(person)
        try:
            p = ldap_schemas.account.objects.get(uid=person.username)
        except ldap_schemas.account.DoesNotExist:
            p = ldap_schemas.person.objects.get(uid=person.username)
        p.givenName = person.first_name
        p.sn = person.last_name
        p.telephoneNumber = str_or_none(person.telephone)
        p.mail = str_or_none(person.email)
        p.title = str_or_none(person.title)
        p.o = person.institute.name
        p.pre_save()
        p.save()

    def lock_user(self, person):
        super(PersonalDataStore, self).lock_user(person)
        p = ldap_schemas.person.objects.get(uid=person.username)
        p.lock()
        p.pre_save()
        p.save()

    def unlock_user(self, person):
        super(PersonalDataStore, self).unlock_user(person)
        p = ldap_schemas.person.objects.get(uid=person.username)
        p.unlock()
        p.pre_save()
        p.save()

    def set_password(self, person, raw_password):
        super(PersonalDataStore, self).set_password(person, raw_password)
        p = ldap_schemas.person.objects.get(uid=person.username)
        p.change_password(raw_password)
        p.pre_save()
        p.save()

    def user_exists(self, username):
        try:
            ldap_schemas.person.objects.get(uid=username)
            return True
        except ldap_schemas.person.DoesNotExist:
            return False

    def create_password_hash(self, raw_password):
        from placard.ldap_passwd import md5crypt
        return '{crypt}%s' % md5crypt(raw_password)

    def change_username(self, person, new_username):
        p = ldap_schemas.person.objects.get(uid=person.username)
        p.rename(uid=new_username)


class AccountDataStore(base.AccountDataStore):

    def create_account(self, person, default_project):
        luser = ldap_schemas.account.objects.convert(ldap_schemas.person).get(uid=person.username)
        luser.set_defaults()
        luser.gidNumber = person.institute.gid
        luser.homeDirectory = settings.HOME_DIRECTORY % { 'default_project': default_project.pid, 'uid': luser.uid }
        luser.pre_create(master=None)
        luser.pre_save()
        luser.save()

        ua = super(AccountDataStore, self).create_account(person, default_project)
        return ua

    def delete_account(self, ua):
        super(AccountDataStore, self).delete_account(ua)
        luser = ldap_schemas.account.objects.get(uid=ua.username)
        luser.pre_delete()
        luser.delete()

    def update_account(self, ua):
        super(AccountDataStore, self).update_account(ua)
        luser = ldap_schemas.account.objects.get(uid=ua.username)
        luser.gidNumber = ua.user.institute.gid
        luser.pre_save()
        luser.save()

    def lock_account(self, ua):
        super(AccountDataStore, self).lock_account(ua)

    def unlock_account(self, ua):
        super(AccountDataStore, self).unlock_account(ua)

    def get_shell(self, ua):
        luser = ldap_schemas.account.objects.get(uid=ua.username)
        return luser.loginShell

    def change_shell(self, ua, shell):
        super(AccountDataStore, self).change_shell(ua, shell)
        luser = ldap_schemas.account.objects.get(uid=ua.username)
        luser.loginShell = shell
        luser.pre_save()
        luser.save()
