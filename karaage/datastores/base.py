# Copyright 2008, 2010-2011, 2013-2015 VPAC
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


class GlobalDataStore(object):

    """ Base class used for all global datastores. """

    def __init__(self, config):
        self.config = config

    ##########
    # PERSON #
    ##########

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

    def add_person_to_group(self, person, group):
        """ Add person to group. """
        return

    def remove_person_from_group(self, person, group):
        """ Remove person from group. """
        return

    def get_person_details(self, person):
        """ Get person's details. """
        return {}

    def person_exists(self, username):
        """ Does the person exist? """
        return False

    #########
    # GROUP #
    #########

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


class MachineCategoryDataStore(object):
    """ Base class used for all MC datastores. """

    def __init__(self, config):
        self.config = config

    ###########
    # ACCOUNT #
    ###########

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

    def add_account_to_group(self, account, group):
        """ Add account to group. """
        return

    def remove_account_from_group(self, account, group):
        """ Remove account from group. """
        return

    def add_account_to_project(self, account, project):
        """ Add account to project. """
        return

    def remove_account_from_project(self, account, project):
        """ Remove account from project. """
        return

    def add_account_to_institute(self, account, institute):
        """ Add account to institute. """
        return

    def remove_account_from_institute(self, account, institute):
        """ Remove account from institute. """
        return

    def account_exists(self, username):
        """ Does the account exist? """
        return False

    def get_account_details(self, account):
        """ Get the account details """
        return {}

    #########
    # GROUP #
    #########

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

    ###########
    # PROJECT #
    ###########

    def save_project(self, project):
        """ Project was saved. """
        return

    def delete_project(self, project):
        """ Project was deleted. """
        return

    def get_project_details(self, project):
        """ Get project's details. """
        return {}

    def set_project_pid(self, project, old_pid, new_pid):
        """ Project's pid was changed. """
        return

    #############
    # INSTITUTE #
    #############

    def save_institute(self, institute):
        """ Institute was saved. """
        return

    def delete_institute(self, institute):
        """ Institute was deleted. """
        return

    def get_institute_details(self, institute):
        """ Get institute's details. """
        return {}
