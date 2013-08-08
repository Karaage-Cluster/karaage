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

""" Base file used for all datastores. """


class PersonDataStore(object):
    """ Base class used for all personal datastores. """

    def __init__(self, config):
        self.config = config

    def save_person(self, person):
        """ Person was saved. """
        return

    def delete_person(self, person):
        """ Person was deleted. """
        return

    def set_person_password(self, person, raw_password):
        """ Person's password was changed. """
        return

    def set_person_username(self, person, old_username, new_username):
        """ Person's username was changed. """
        return

    def get_person_details(self, person):
        """ Get person's details. """
        return {}

    def person_exists(self, username):
        """ Does the person exist? """
        return False


class AccountDataStore(object):
    """ Base class used for all account datastores. """

    def __init__(self, config):
        self.config = config

    def save_account(self, account):
        """ Account was saved. """
        return

    def delete_account(self, account):
        """ Account was deleted. """
        return

    def set_account_password(self, account, raw_password):
        """ Account's password was changed. """
        return

    def set_account_username(self, account, old_username, new_username):
        """ Account's username was changed. """
        return

    def account_exists(self, username):
        """ Does the account exist? """
        return False

    def get_account_details(self, account):
        """ Get the account details """
        return {}

    def add_account_to_group(self, account, group):
        """ Add account to group. """
        return

    def remove_account_from_group(self, account, group):
        """ Remove account from group. """
        return

    def save_group(self, group):
        """ Group was saved. """
        return

    def delete_group(self, group):
        """ Group was deleted. """
        return

    def set_group_name(self, group, old_name, new_name):
        """ Group was renamed. """
        return

    def get_group_details(self, group):
        """ Get the group details. """
        return {}


class ProjectDataStore:
    """ Base clase for project datastores. """

    def __init__(self, config):
        self.config = config

    def save_project(self, project):
        """ Project was saved. """
        return

    def delete_project(self, project):
        """ Project was deleted. """
        return


class InstituteDataStore:
    """ Base clase for institute datastores. """

    def __init__(self, config):
        self.config = config

    def save_institute(self, institute):
        """ Institute was saved. """
        return

    def delete_institute(self, institute):
        """ Institute was deleted. """
        return


class SoftwareDataStore:
    """ Base clase for software datastores. """

    def __init__(self, config):
        self.config = config

    def save_software(self, software):
        """ Software was saved. """
        return

    def delete_software(self, software):
        """ Software was deleted. """
        return
