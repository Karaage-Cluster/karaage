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

""" Common hooks for all datastores. """

from django.conf import settings
import django.utils

_DATASTORES = {}

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

def _init_datastores():
    """ Initialize all datastores. """
    for name, array in settings.DATASTORES.iteritems():
        _DATASTORES[name] = []
        for config in array:
            cls = _lookup(config['ENGINE'])
            _DATASTORES[name].append(cls(config))

def _get_datastores_for_name(name):
    """ Get the datastores for name. """
    return _DATASTORES[name]

def _get_all_names():
    """ Get all datstores that are in use. """
    from karaage.machines.models import MachineCategory
    for machine_category in MachineCategory.objects.all():
        yield machine_category.datastore

# Initialize data stores
_init_datastores()


##########
# PERSON #
##########

def save_person(person):
    """ Person was saved. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.save_person(person)

def delete_person(person):
    """ Person was deleted. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.delete_person(person)

def set_person_password(person, raw_password):
    """ Person's password was changed. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.set_person_password(person, raw_password)

def set_person_username(person, old_username, new_username):
    """ Person's username was changed. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.set_person_username(person, old_username, new_username)

def person_exists(username):
    """ Does this person exist??? """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            if datastore.person_exists(username):
                return True
    return False

def get_person_details(person):
    """ Get details for this user. """
    result = {}
    for name in _get_all_names():
        result[name] = []
        for datastore in _get_datastores_for_name(name):
            value = datastore.get_person_details(person)
            value['datastore'] = datastore.config['DESCRIPTION']
            result[name].append(value)
    return result


###########
# ACCOUNT #
###########

def save_account(account):
    """ Account was saved. """
    name = account.machine_category.datastore
    for datastore in _get_datastores_for_name(name):
        datastore.save_account(account)

def delete_account(account):
    """ Account was deleted. """
    name = account.machine_category.datastore
    for datastore in _get_datastores_for_name(name):
        datastore.delete_account(account)

def set_account_password(account, raw_password):
    """ Account's password was changed. """
    name = account.machine_category.datastore
    for datastore in _get_datastores_for_name(name):
        datastore.set_account_password(account, raw_password)

def set_account_username(account, old_username, new_username):
    """ Account's username was changed. """
    name = account.machine_category.datastore
    for datastore in _get_datastores_for_name(name):
        datastore.set_account_username(account, old_username, new_username)

def account_exists(username, machine_category):
    """ Does the account exist??? """
    name = machine_category.datastore
    for datastore in _get_datastores_for_name(name):
        if datastore.account_exists(username):
            return True
    return False

def get_account_details(account):
    """ Get the account details. """
    result = {}
    name = account.machine_category.datastore
    result[name] = []
    for datastore in _get_datastores_for_name(name):
        value = datastore.get_account_details(account)
        value['datastore'] = datastore.config['DESCRIPTION']
        result[name].append(value)
    return result

def add_account_to_group(account, group):
    """ Add account to group. """
    name = account.machine_category.datastore
    for datastore in _get_datastores_for_name(name):
        datastore.add_account_to_group(account, group)

def remove_account_from_group(account, group):
    """ Remove account from group. """
    name = account.machine_category.datastore
    for datastore in _get_datastores_for_name(name):
        datastore.remove_account_from_group(account, group)


#########
# GROUP #
#########

def save_group(group):
    """ Group was saved. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.save_group(group)

def delete_group(group):
    """ Group was deleted. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.delete_group(group)

def set_group_name(group, old_name, new_name):
    """ Group was renamed. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.set_group_name(group, old_name, new_name)

def get_group_details(group):
    """ Get group details. """
    result = {}
    for name in _get_all_names():
        result[name] = []
        for datastore in _get_datastores_for_name(name):
            value = datastore.get_group_details(group)
            value['datastore'] = datastore.config['DESCRIPTION']
            result[name].append(value)
    return result


###########
# Project #
###########

def save_project(institute):
    """ An institute has been saved. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.save_project(institute)

def delete_project(institute):
    """ An institute has been deleted. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.delete_project(institute)


#############
# Institute #
#############

def save_institute(institute):
    """ An institute has been saved. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.save_institute(institute)

def delete_institute(institute):
    """ An institute has been deleted. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.delete_institute(institute)


############
# Software #
############

def save_software(institute):
    """ An institute has been saved. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.save_software(institute)

def delete_software(institute):
    """ An institute has been deleted. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.delete_software(institute)
