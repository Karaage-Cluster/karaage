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

""" LDAP datastore. """

from karaage.datastores import base

from django.conf import settings
import django.utils

def _str_or_none(string):
    """ Return a string of None if string is empty. """
    if string is None or string == "":
        return None
    return string

def _lookup(cls):
    """ Lookup module.class. """
    if isinstance(cls, str):
        module_name, _, name = cls.rpartition(".")
        module = django.utils.importlib.import_module(module_name)
        try:
            cls = getattr(module, name)
        except AttributeError:
            raise AttributeError("%s reference cannot be found" % cls)
    return(cls)


class AccountDataStore(base.BaseDataStore):
    """ LDAP Account datastore. """

    def __init__(self, config):
        super(AccountDataStore, self).__init__(config)
        self._using = config['LDAP']
        self._account = _lookup(config['ACCOUNT'])
        self._group = _lookup(config['GROUP'])
        self._primary_group = config.get('PRIMARY_GROUP',
                'institute')
        self._default_primary_group = config.get('DEFAULT_PRIMARY_GROUP',
                'dummy')
        self._home_directory = config.get('HOME_DIRECTORY',
                "/home/%(uid)s")
        self._locked_shell = config.get('LOCKED_SHELL',
                "/usr/local/sbin/locked")
        self._settings = config

    def _accounts(self):
        """ Return accounts query. """
        return self._account.objects.using(
                using=self._using, settings=self._settings)

    def _groups(self):
        """ Return groups query. """
        return self._group.objects.using(
                using=self._using, settings=self._settings)

    def _create_account(self):
        """ Create a new account. """
        return self._account(
                using=self._using, settings=self._settings)

    def _create_group(self):
        """ Create a new group. """
        return self._group(
                using=self._using, settings=self._settings)

    def edit_form(self, account):
        """Return the edit form for this account type."""
        from karaage.machines.forms import AccountDetails
        return AccountDetails(account)

    def save_account(self, account):
        """ Account was saved. """
        person = account.person
        if self._primary_group == 'institute':
            lgroup = self._groups().get(cn=person.institute.group.name)
        elif self._primary_group == 'default_project':
            if account.default_project is None:
                lgroup = self._groups().get(cn=self._default_primary_group)
            else:
                lgroup = self._groups().get(
                    cn=account.default_project.group.name)
        else:
            raise RuntimeError("Unknown value of PRIMARY_GROUP.")

        if account.default_project is None:
            default_project = "none"
        else:
            default_project = account.default_project.pid

        try:
            luser = self._accounts().get(uid=account.username)
            luser.gidNumber = lgroup.gidNumber
            luser.givenName = person.first_name
            luser.sn = person.last_name
            luser.fullName = person.full_name
            luser.telephoneNumber = _str_or_none(person.telephone)
            luser.mail = _str_or_none(person.email)
            luser.title = _str_or_none(person.title)
            luser.o = person.institute.name
            luser.gidNumber = lgroup.gidNumber
            luser.homeDirectory = self._home_directory % {
                'default_project': default_project,
                'uid': person.username }
            if account.is_locked():
                luser.loginShell = self._locked_shell
                luser.lock()
            else:
                luser.loginShell = account.shell
                luser.unlock()
            luser.save()
        except self._account.DoesNotExist:
            luser = self._create_account()
            luser.uid = person.username
            luser.givenName = person.first_name
            luser.sn = person.last_name
            luser.fullName = person.full_name
            luser.telephoneNumber = _str_or_none(person.telephone)
            luser.mail = _str_or_none(person.email)
            luser.title = _str_or_none(person.title)
            luser.o = person.institute.name
            luser.gidNumber = lgroup.gidNumber
            luser.homeDirectory = self._home_directory % {
                'default_project': default_project,
                'uid': person.username }
            if account.is_locked():
                luser.loginShell = self._locked_shell
                luser.lock()
            else:
                luser.loginShell = account.shell
                luser.unlock()
            luser.save()

            # add all groups
            for group in account.person.groups.all():
                self.add_account_to_group(account, group)

    def delete_account(self, account):
        """ Account was deleted. """
        try:
            luser = self._accounts().get(uid=account.username)
            luser.secondary_groups.clear()
            luser.delete()
        except self._account.DoesNotExist:
            # it doesn't matter if it doesn't exist
            pass

    def set_account_password(self, account, raw_password):
        """ Account's password was changed. """
        luser = self._accounts().get(uid=account.username)
        luser.change_password(raw_password)
        luser.save()

    def set_account_username(self, account, old_username, new_username):
        """ Account's username was changed. """
        luser = self._accounts().get(uid=old_username)
        luser.rename(uid=new_username)

    def add_account_to_group(self, account, group):
        """ Add account to group. """
        lgroup = self._groups().get(cn=group.name)
        person = self._accounts().get(uid=account.username)
        lgroup.secondary_accounts.add(person)

    def remove_account_from_group(self, account, group):
        """ Remove account from group. """
        lgroup = self._groups().get(cn=group.name)
        person = self._accounts().get(uid=account.username)
        lgroup.secondary_accounts.remove(person)

    def get_account_details(self, account):
        """ Account's details were changed. """
        luser = self._accounts().get(uid=account.username)
        result = {}
        for i, j in luser.get_fields():
            if i != 'userPassword' and j is not None:
                result[i] = j
        result['dn'] = luser.dn
        group = luser.primary_group.get_obj()
        if group is not None:
            result['primary_group'] = group.dn
        result['secondary_groups'] = [
                g.dn for g in luser.secondary_groups.all() ]
        return result

    def account_exists(self, username):
        """ Account's details were changed. """
        try:
            self._accounts().get(uid=username)
            return True
        except self._account.DoesNotExist:
            return False

    def save_group(self, group):
        """ Group was saved. """
        # if group already exists, take over existing group rather then error.
        try:
            lgroup = self._groups().get(cn=group.name)
            lgroup.description = group.description
            lgroup.save()
        except self._group.DoesNotExist:
            lgroup = self._create_group()
            lgroup.cn = group.name
            lgroup.description = group.description
            lgroup.save()

    def delete_group(self, group):
        """ Group was deleted. """
        try:
            lgroup = self._groups().get(cn=group.name)
            lgroup.delete()
        except self._group.DoesNotExist:
            # it doesn't matter if it doesn't exist
            pass

    def set_group_name(self, group, old_name, new_name):
        """ Group was renamed. """
        lgroup = self._groups().get(cn=old_name)
        lgroup.rename(cn=new_name)

    def get_group_details(self, group):
        """ Get the group details. """
        lgroup = self._groups().get(cn=group.name)
        result = {}
        for i, j in lgroup.get_fields():
            if j is not None:
                result[i] = j
        result['dn'] = lgroup.dn
        result['primary_accounts'] = [
                a.dn for a in lgroup.primary_accounts.all() ]
        result['secondary_accounts'] = [
                a.dn for a in lgroup.secondary_accounts.all() ]
        return result
