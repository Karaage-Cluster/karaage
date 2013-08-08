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
        raise NotImplementedError

    def delete_person(self, person):
        """ Person was deleted. """
        raise NotImplementedError

    def set_person_password(self, person, raw_password):
        """ Person's password was changed. """
        raise NotImplementedError

    def set_person_username(self, person, old_username, new_username):
        """ Person's username was changed. """
        raise NotImplementedError

    def get_person_details(self, person):
        """ Get person's details. """
        raise NotImplementedError

    def person_exists(self, username):
        """ Does the person exist? """
        raise NotImplementedError


class AccountDataStore(object):
    """ Base class used for all account datastores. """

    def __init__(self, config):
        self.config = config

    def save_account(self, account):
        """ Account was saved. """
        raise NotImplementedError

    def delete_account(self, account):
        """ Account was deleted. """
        raise NotImplementedError

    def set_account_password(self, account, raw_password):
        """ Account's password was changed. """
        raise NotImplementedError

    def set_account_username(self, account, old_username, new_username):
        """ Account's username was changed. """
        raise NotImplementedError

    def account_exists(self, username):
        """ Does the account exist? """
        raise NotImplementedError

    def get_account_details(self, account):
        """ Get the account details """
        raise NotImplementedError

    def add_group(self, account, group):
        """ Add account to group. """
        raise NotImplementedError

    def remove_group(self, account, group):
        """ Remove account from group. """
        raise NotImplementedError

    def save_group(self, group):
        """ Group was saved. """
        raise NotImplementedError

    def delete_group(self, group):
        """ Group was deleted. """
        raise NotImplementedError

    def set_group_name(self, group, old_name, new_name):
        """ Group was renamed. """
        raise NotImplementedError

    def get_group_details(self, group):
        """ Get the group details. """
        raise NotImplementedError


class ProjectDataStore:
    """ Base clase for project datastores. """

    def __init__(self, config):
        pass

    def save_project(self, project):
        """ Project was saved. """
        raise NotImplementedError

    def delete_project(self, project):
        """ Project was deleted. """
        raise NotImplementedError


class InstituteDataStore:
    """ Base clase for institute datastores. """

    def __init__(self, config):
        pass

    def save_institute(self, institute):
        """ Institute was saved. """
        raise NotImplementedError

    def delete_institute(self, institute):
        """ Institute was deleted. """
        raise NotImplementedError


class SoftwareDataStore:
    """ Base clase for software datastores. """

    def __init__(self, config):
        pass

    def save_software(self, software):
        """ Software was saved. """
        raise NotImplementedError

    def delete_software(self, software):
        """ Software was deleted. """
        raise NotImplementedError
