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

""" Save account information in /etc/passwd and /etc/group files. """

from django.conf import settings
from karaage.datastores import base


class AccountDataStore(base.AccountDataStore):
    """ File account datastore. """

    def __init__(self, config):
        super(AccountDataStore, self).__init__(config)
        self.passwd_file = config['PASSWD_FILE']
        self.group_file = config['GROUP_FILE']

    def save_account(self, account):
        """ Account was saved. """
        if account.is_locked():
            login_shell = settings.LOCKED_SHELL
        else:
            login_shell = account.shell

        if self.account_exists():
            super(AccountDataStore, self).update_account(account)

            fobj = open(self.passwd_file)
            data = fobj.readlines()
            fobj.close()
            new_data = []
            for line in data:
                if line.find(account.username) == 0:
                    username, shad, uid, gid, name, homedir, shell = line.split(':')
                    homedir = '/home/%s' % account.username
                    line = "%s:x:%s:%s:%s:%s:%s\n" % (account.username, uid, account.user.institute.gid, account.user.get_full_name(), homedir, login_shell)
                new_data.append(line)

            fobj = open(self.passwd_file, 'w')
            fobj.writelines(new_data)
            fobj.close()
        else:
            person = account.user

            home_dir = '/home/%s' % account.username
            userid = self.get_next_uid()

            line = "%s:x:%s:%s:%s:%s:%s\n" % (account.username, userid, person.institute.gid, person.get_full_name(), home_dir, login_shell)

            fobj = open(self.passwd_file, 'a')
            fobj.write(line)
            fobj.close()

    def delete_account(self, account):
        """ Account was deleted. """
        fobj = open(self.passwd_file)
        data = fobj.readlines()
        fobj.close()
        new_data = []
        for line in data:
            if line.find(account.username) != 0:
                new_data.append(line)

        fobj = open(file, 'w')
        fobj.writelines(new_data)
        fobj.close()

    def change_account_shell(self, account, shell):
        """ Account's shell was changed. """
        super(AccountDataStore, self).change_account_shell(account, shell)
        if account.is_locked():
            login_shell = settings.LOCKED_SHELL
        # FIXME

    def get_next_uid(self):
        """ Pick the next uid to use. """
        id_list = []

        fobj = open(self.passwd_file)
        data = fobj.readlines()
        fobj.close()
        for line in data:
            try:
                id_list.append(int(line.split(':')[2]))
            except:
                pass

        id_list.sort()
        account_id = id_list[-1] + 1

        if account_id < settings.UID_START:
            return settings.UID_START
        else:
            return account_id

    def set_account_password(self, account, raw_password):
        """ Account's password was changed. """
        # FIXME
        pass

    def change_account_username(self, account, old_username, new_username):
        """ Account's username was changed. """
        # FIXME
        pass

    def account_exists(self, username):
        """ Does the account exist? """
        # FIXME
        pass

    def get_account_details(self, account):
        """ Get account details. """
        # FIXME
        pass

    def add_group(self, account, group):
        """ Add account to group. """
        # FIXME
        pass

    def remove_group(self, account, group):
        """ Remove account from group. """
        # FIXME
        pass

    def save_group(self, group):
        """ Group was saved. """
        # FIXME
        pass

    def delete_group(self, group):
        """ Group was deleted. """
        # FIXME
        pass

    def change_group_name(self, group, old_name, new_name):
        """ Group was renamed. """
        # FIXME
        pass

    def get_group_details(self, group):
        """ Get the group details. """
        # FIXME
        pass
