# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
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

""" Common hooks for all datastores. """

import importlib
import types
import warnings

from django.conf import settings

from .base import DataStore

_DATASTORES = []


def _lookup(cls):
    """ Lookup module.class. """
    if isinstance(cls, str):
        module_name, _, name = cls.rpartition(".")
        module = importlib.import_module(module_name)
        try:
            cls = getattr(module, name)
        except AttributeError:
            raise AttributeError("%s reference cannot be found" % cls)
    return cls


def _get_datastore(cls, expected, config):
    assert isinstance(cls, types.FunctionType) or issubclass(cls, expected)
    ds = cls(config)
    assert isinstance(ds, expected)
    return ds


def _init_datastores():
    """ Initialize all datastores. """
    global _DATASTORES
    array = settings.DATASTORES
    for config in array:
        cls = _lookup(config['ENGINE'])
        ds = _get_datastore(cls, DataStore, config)
        _DATASTORES.append(ds)
    legacy_settings = getattr(settings, 'MACHINE_CATEGORY_DATASTORES', None)
    if legacy_settings is not None:
        warnings.warn(
            "MACHINE_CATEGORY_DATASTORES is deprecated, "
            "please change to use DATASTORES",
        )
        for name in ['ldap']:
            array = settings.MACHINE_CATEGORY_DATASTORES.get(name, [])
            for config in array:
                cls = _lookup(config['ENGINE'])
                ds = _get_datastore(cls, DataStore, config)
                _DATASTORES.append(ds)


def _get_datastores():
    global _DATASTORES
    return _DATASTORES


# Initialize data stores
_init_datastores()


######################################################################
# DATASTORES                                                         #
######################################################################


###########
# Account #
###########

def save_account(account):
    """ Account was saved. """
    for datastore in _get_datastores():
        datastore.save_account(account)


def delete_account(account):
    """ Account was deleted. """
    for datastore in _get_datastores():
        datastore.delete_account(account)


def set_account_password(account, raw_password):
    """ Account's password was changed. """
    for datastore in _get_datastores():
        datastore.set_account_password(account, raw_password)


def set_account_username(account, old_username, new_username):
    """ Account's username was changed. """
    for datastore in _get_datastores():
        datastore.set_account_username(account, old_username, new_username)


def add_account_to_group(account, group):
    """ Add account to group. """
    for datastore in _get_datastores():
        datastore.add_account_to_group(account, group)


def remove_account_from_group(account, group):
    """ Remove account from group. """
    for datastore in _get_datastores():
        datastore.remove_account_from_group(account, group)


def add_account_to_project(account, project):
    """ Add account to project. """
    for datastore in _get_datastores():
        datastore.add_account_to_project(account, project)


def remove_account_from_project(account, project):
    """ Remove account from project. """
    for datastore in _get_datastores():
        datastore.remove_account_from_project(account, project)


def add_account_to_institute(account, institute):
    """ Add account to institute. """
    for datastore in _get_datastores():
        datastore.add_account_to_institute(account, institute)


def remove_account_from_institute(account, institute):
    """ Remove account from institute. """
    for datastore in _get_datastores():
        datastore.remove_account_from_institute(account, institute)


def account_exists(username):
    """ Does the account exist??? """
    for datastore in _get_datastores():
        if datastore.account_exists(username):
            return True
    return False


def get_account_details(account):
    """ Get the account details. """
    result = []
    for datastore in _get_datastores():
        value = datastore.get_account_details(account)
        value['datastore'] = datastore.config['DESCRIPTION']
        result.append(value)
    return result


#########
# Group #
#########

def save_group(group):
    """ Group was saved. """
    for datastore in _get_datastores():
        datastore.save_group(group)


def delete_group(group):
    """ Group was deleted. """
    for datastore in _get_datastores():
        datastore.delete_group(group)


def set_group_name(group, old_name, new_name):
    """ Group was renamed. """
    for datastore in _get_datastores():
        datastore.set_group_name(group, old_name, new_name)


def get_group_details(group):
    """ Get group details. """
    result = []
    for datastore in _get_datastores():
        value = datastore.get_group_details(group)
        value['datastore'] = datastore.config['DESCRIPTION']
        result.append(value)
    return result


###########
# Project #
###########

def save_project(project):
    """ An machine has been saved. """
    for datastore in _get_datastores():
        datastore.save_project(project)


def delete_project(project):
    """ An machine has been deleted. """
    for datastore in _get_datastores():
        datastore.delete_project(project)


def get_project_details(project):
    """ Get details for this user. """
    result = []
    for datastore in _get_datastores():
        value = datastore.get_project_details(project)
        value['datastore'] = datastore.config['DESCRIPTION']
        result.append(value)
    return result


def set_project_pid(project, old_pid, new_pid):
    """ Project's PID was changed. """
    for datastore in _get_datastores():
        datastore.save_project(project)
        datastore.set_project_pid(project, old_pid, new_pid)


#############
# Institute #
#############

def save_institute(institute):
    """ An institute has been saved. """
    for datastore in _get_datastores():
        datastore.save_institute(institute)


def delete_institute(institute):
    """ An institute has been deleted. """
    for datastore in _get_datastores():
        datastore.delete_institute(institute)


def get_institute_details(institute):
    """ Get details for this user. """
    result = []
    for datastore in _get_datastores():
        value = datastore.get_institute_details(institute)
        value['datastore'] = datastore.config['DESCRIPTION']
        result.append(value)
    return result


######################################################################
# OTHER                                                              #
######################################################################

def add_accounts_to_group(accounts_query, group):
    """ Add accounts to group. """

    query = accounts_query.filter(date_deleted__isnull=True)

    for account in query:
        add_account_to_group(account, group)


def remove_accounts_from_group(accounts_query, group):
    """ Remove accounts from group. """

    query = accounts_query.filter(date_deleted__isnull=True)

    for account in query:
        remove_account_from_group(account, group)


def add_accounts_to_project(accounts_query, project):
    """ Add accounts to project. """

    query = accounts_query.filter(date_deleted__isnull=True)

    for account in query:
        add_account_to_project(account, project)


def remove_accounts_from_project(accounts_query, project):
    """ Remove accounts from project. """

    query = accounts_query.filter(date_deleted__isnull=True)

    for account in query:
        remove_account_from_project(account, project)


def add_accounts_to_institute(accounts_query, institute):
    """ Add accounts to institute. """

    query = accounts_query.filter(date_deleted__isnull=True)

    for account in query:
        add_account_to_institute(account, institute)


def remove_accounts_from_institute(accounts_query, institute):
    """ Remove accounts from institute. """

    query = accounts_query.filter(date_deleted__isnull=True)

    for account in query:
        remove_account_from_institute(account, institute)
