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

    def save_account(self, ua):
        super(AccountDataStore, self).save_account(ua)

        person = ua.user
        lgroup = ldap_schemas.group.objects.get(cn=person.institute.group.name)

        try:
            luser = ldap_schemas.account.objects.get(uid=ua.username)
            luser.gidNumber = lgroup.gidNumber
            luser.givenName = person.first_name
            luser.sn = person.last_name
            luser.telephoneNumber = str_or_none(person.telephone)
            luser.mail = str_or_none(person.email)
            luser.title = str_or_none(person.title)
            luser.o = person.institute.name
            luser.gidNumber = lgroup.gidNumber
            luser.homeDirectory = settings.HOME_DIRECTORY % { 'default_project': ua.default_project.pid, 'uid': person.username }
            if ua.is_locked():
                luser.loginShell = settings.LOCKED_SHELL
            else:
                luser.loginShell = ua.shell
            luser.pre_save()
            luser.save()
        except ldap_schemas.account.DoesNotExist:
            luser = ldap_schemas.account()
            luser.set_defaults()
            luser.uid = person.username
            luser.givenName = person.first_name
            luser.sn = person.last_name
            luser.telephoneNumber = str_or_none(person.telephone)
            luser.mail = str_or_none(person.email)
            luser.title = str_or_none(person.title)
            luser.o = person.institute.name
            luser.gidNumber = lgroup.gidNumber
            luser.homeDirectory = settings.HOME_DIRECTORY % { 'default_project': ua.default_project.pid, 'uid': person.username }
            luser.loginShell = ua.shell
            luser.pre_create(master=None)
            luser.pre_save()
            luser.save()

            # add all groups
            for group in ua.user.groups.all():
                self.add_group(ua, group)


    def delete_account(self, ua):
        super(AccountDataStore, self).delete_account(ua)
        luser = ldap_schemas.account.objects.get(uid=ua.username)
        luser.secondary_groups.clear()
        luser.pre_delete()
        luser.delete()

    def lock_account(self, ua):
        super(AccountDataStore, self).lock_account(ua)

    def unlock_account(self, ua):
        super(AccountDataStore, self).unlock_account(ua)

    def change_account_shell(self, ua, shell):
        super(AccountDataStore, self).change_account_shell(ua, shell)
        luser = ldap_schemas.account.objects.get(uid=ua.username)
        if ua.is_locked():
            luser.loginShell = settings.LOCKED_SHELL
        else:
            luser.loginShell = shell
        luser.pre_save()
        luser.save()

    def set_user_password(self, ua, raw_password):
        super(AccountDataStore, self).set_user_password(ua, raw_password)
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

    def change_user_username(self, ua, old_username, new_username):
        super(AccountDataStore, self).change_user_username(ua, old_username, new_username)
        p = ldap_schemas.account.objects.get(uid=old_username)
        p.rename(uid=new_username)

    def get_account_details(self, ua):
        p = ldap_schemas.account.objects.get(uid=ua.username)
        result = {}
        for i, j in p.get_fields():
            if i != 'userPassword' and j is not None:
                result[i] = j
        result['dn'] = p.dn
        group = p.primary_group.get_obj()
        if group is not None:
            result['primary_group'] = group.dn
        result['secondary_groups'] = [ g.dn for g in p.secondary_groups.all() ]
        return result

    def add_group(self, ua, group):
        lgroup = ldap_schemas.group.objects.get(cn=group.name)
        person = ldap_schemas.account.objects.get(uid=ua.username)
        lgroup.secondary_accounts.add(person)
        pass

    def remove_group(self, ua, group):
        lgroup = ldap_schemas.group.objects.get(cn=group.name)
        person = ldap_schemas.account.objects.get(uid=ua.username)
        lgroup.secondary_accounts.remove(person)

    def save_group(self, group):
        # if group already exists, take over existing group rather then error.
        try:
            lgroup = ldap_schemas.group.objects.get(cn=group.name)
            lgroup.description = group.description
            lgroup.pre_save()
            lgroup.save()
        except ldap_schemas.group.DoesNotExist:
            lgroup = ldap_schemas.group(cn=group.name)
            lgroup.set_defaults()
            lgroup.description = group.description
            lgroup.pre_create(master=None)
            lgroup.pre_save()
            lgroup.save()

    def delete_group(self, group):
        lgroup = ldap_schemas.group.objects.get(cn=group.name)
        lgroup.delete()

    def change_group_name(self, group, old_name, new_name):
        super(AccountDataStore, self).change_group_name(group, old_name, new_name)
        lgroup = ldap_schemas.group.objects.get(cn=old_name)
        lgroup.rename(cn=new_name)

    def get_group_details(self, group):
        lgroup = ldap_schemas.group.objects.get(cn=group.name)
        result = {}
        for i, j in lgroup.get_fields():
            if j is not None:
                result[i] = j
        result['dn'] = lgroup.dn
        result['primary_accounts'] = [ a.dn for a in lgroup.primary_accounts.all() ]
        result['secondary_accounts'] = [ a.dn for a in lgroup.secondary_accounts.all() ]
        return result
