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

from django.conf import settings

from karaage.datastores import base
from karaage.datastores import ldap_models

def str_or_none(string):
    if string is None or string == "":
        return None
    return ""

class PersonalDataStore(base.PersonalDataStore):
    
    def create_new_user(self, data, hashed_password):
        return super(PersonalDataStore, self).create_new_user(data, hashed_password)

    def activate_user(self, person):
        person = super(PersonalDataStore, self).activate_user(person)

        p = ldap_models.person()
        p.set_defaults()
        p.uid = person.username
        p.givenName = person.first_name
        p.sn = person.last_name
        p.telephoneNumber = str_or_none(person.telephone) or None
        p.mail = str_or_none(person.email) or None
        p.title = str_or_none(person.title) or None
        p.o = person.institute.name
        p.userPassword = person.user.password
        p.save()

        return person

    def delete_user(self, person):
        super(PersonalDataStore, self).delete_user(person)
        try:
            p = ldap_models.person.objects.get(uid=person.username)
            p.delete()
        except ldap_models.person.DoesNotExist:
            pass

    def update_user(self, person):
        super(PersonalDataStore, self).update_user(person)
        p = ldap_models.person.objects.get(uid=person.username)
        p.givenName = person.first_name
        p.sn = person.last_name
        p.telephoneNumber = str_or_none(person.telephone) or None
        p.mail = str_or_none(person.email) or None
        p.title = str_or_none(person.title) or None
        p.o = person.institute.name
        p.save()

    def is_locked(self, person):
        p = ldap_models.person.objects.get(uid=person.username)
        return p.is_locked()

    def lock_user(self, person):
        super(PersonalDataStore, self).lock_user(person)
        p = ldap_models.person.objects.get(uid=person.username)
        p.lock()
        p.save()

    def unlock_user(self, person):
        super(PersonalDataStore, self).unlock_user(person)
        p = ldap_models.person.objects.get(uid=person.username)
        p.unlock()
        p.save()

    def set_password(self, person, raw_password):
        super(PersonalDataStore, self).set_password(person, raw_password)
        p = ldap_models.person.objects.get(uid=person.username)
        p.change_password(raw_password, settings.LDAP_PASSWD_SCHEME)
        p.save()

    def user_exists(self, username):
        try:
            p = ldap_models.person.objects.get(uid=username)
            return True
        except ldap_models.person.DoesNotExist:
            return False

    def create_password_hash(self, raw_password):
        from placard.ldap_passwd import md5crypt
        return '{crypt}%s' % md5crypt(raw_password)

    def change_username(self, person, new_username):
        p = ldap_models.person.objects.get(uid=person.username)
        p.rename(uid=new_username)


class AccountDataStore(base.AccountDataStore):

    def create_account(self, person, default_project):
        luser = ldap_models.account.objects.convert(ldap_models.person).get(uid=person.username)
        luser.set_defaults()
        luser.gidNumber = person.institute.gid
        luser.save()

        ua = super(AccountDataStore, self).create_account(person, default_project)
        return ua

    def delete_account(self, ua):
        super(AccountDataStore, self).delete_account(ua)
        luser = ldap_models.account.objects.get(uid=ua.username)
        luser.delete()

    def update_account(self, ua):
        super(AccountDataStore, self).update_account(ua)
        luser = ldap_models.account.objects.get(uid=ua.username)
        luser.gidNumber = ua.user.institute.gid
        luser.save()

    def lock_account(self, ua):
        super(AccountDataStore, self).lock_account(ua)

    def unlock_account(self, ua):
        super(AccountDataStore, self).unlock_account(ua)

    def get_shell(self, ua):
        luser = ldap_models.account.objects.get(uid=ua.username)
        return luser.loginShell

    def change_shell(self, ua, shell):
        super(AccountDataStore, self).change_shell(ua, shell)
        luser = ldap_models.account.objects.get(uid=ua.username)
        luser.loginShell = shell
        luser.save()
