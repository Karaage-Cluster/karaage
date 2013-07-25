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

""" Common hooks for personal and account datastores. """

from django.conf import settings

_PERSONAL_DATASTORES = {}
_ACCOUNT_DATASTORES = {}

def _init_datastores():
    """ Initialize all datastores. """
    for name, array in settings.PERSONAL_DATASTORES.iteritems():
        _PERSONAL_DATASTORES[name] = []
        for config in array:
            module = __import__(config['ENGINE'], {}, {}, [''])
            _PERSONAL_DATASTORES[name].append(module.PersonalDataStore(config))
    for name, array in settings.ACCOUNT_DATASTORES.iteritems():
        _ACCOUNT_DATASTORES[name] = []
        for config in array:
            module = __import__(config['ENGINE'], {}, {}, [''])
            _ACCOUNT_DATASTORES[name].append(module.AccountDataStore(config))

def _get_personal_datastores():
    """ Get the default personal datastores. """
    name = settings.PERSONAL_DATASTORE
    return _PERSONAL_DATASTORES[name]

def _get_account_datastores(name):
    """ Get the account datastores. """
    return _ACCOUNT_DATASTORES[name]


def save_user(person):
    """ Person was saved. """
    for datastore in _get_personal_datastores():
        datastore.save_user(person)

def delete_user(person):
    """ Person was deleted. """
    for datastore in _get_personal_datastores():
        datastore.delete_user(person)

def lock_user(person):
    """ Person was locked. """
    for datastore in _get_personal_datastores():
        datastore.lock_user(person)

def unlock_user(person):
    """ Person was unlocked. """
    for datastore in _get_personal_datastores():
        datastore.unlock_user(person)

def set_user_password(person, raw_password):
    """ Person's password was changed. """
    for datastore in _get_personal_datastores():
        datastore.set_user_password(person, raw_password)

def change_user_username(person, old_username, new_username):
    """ Person's username was changed. """
    for datastore in _get_personal_datastores():
        datastore.change_user_username(person, old_username, new_username)

def user_exists(username):
    """ Does this person exist??? """
    for datastore in _get_personal_datastores():
        if datastore.user_exists(username):
            return True
    return False

def get_user_details(person):
    """ Get details for this user. """
    result = []
    for datastore in _get_personal_datastores():
        value = datastore.get_user_details(person)
        value['datastore'] = datastore.config['DESCRIPTION']
        result.append(value)
    return result


def save_account(account):
    """ Account was saved. """
    name = account.machine_category.datastore
    for datastore in _get_account_datastores(name):
        datastore.save_account(account)

def delete_account(account):
    """ Account was deleted. """
    name = account.machine_category.datastore
    for datastore in _get_account_datastores(name):
        datastore.delete_account(account)

def lock_account(account):
    """ Account was locked. """
    name = account.machine_category.datastore
    for datastore in _get_account_datastores(name):
        datastore.lock_account(account)

def unlock_account(account):
    """ Account was unlocked. """
    name = account.machine_category.datastore
    for datastore in _get_account_datastores(name):
        datastore.unlock_account(account)

def change_account_shell(account, shell):
    """ Account's shell was changed. """
    name = account.machine_category.datastore
    for datastore in _get_account_datastores(name):
        datastore.change_account_shell(account, shell)

def set_account_password(account, raw_password):
    """ Account's password was changed. """
    name = account.machine_category.datastore
    for datastore in _get_account_datastores(name):
        datastore.set_user_password(account, raw_password)

def change_account_username(account, old_username, new_username):
    """ Account's username was changed. """
    name = account.machine_category.datastore
    for datastore in _get_account_datastores(name):
        datastore.change_user_username(account, old_username, new_username)

def account_exists(username, machine_category):
    """ Does the account exist??? """
    name = machine_category.datastore
    for datastore in _get_account_datastores(name):
        if datastore.account_exists(username):
            return True
    return False

def get_account_details(account):
    """ Get the account details. """
    result = []
    name = account.machine_category.datastore
    for datastore in _get_account_datastores(name):
        value = datastore.get_account_details(account)
        value['datastore'] = datastore.config['DESCRIPTION']
        result.append(value)
    return result


def add_group(account, group):
    """ Add account to group. """
    from karaage.machines.models import MachineCategory
    for machine_category in MachineCategory.objects.all():
        name = machine_category.datastore
        for datastore in _get_account_datastores(name):
            datastore.add_group(account, group)

def remove_group(account, group):
    """ Remove account from group. """
    from karaage.machines.models import MachineCategory
    for machine_category in MachineCategory.objects.all():
        name = machine_category.datastore
        for datastore in _get_account_datastores(name):
            datastore.remove_group(account, group)

def save_group(group):
    """ Group was saved. """
    from karaage.machines.models import MachineCategory
    for machine_category in MachineCategory.objects.all():
        name = machine_category.datastore
        for datastore in _get_account_datastores(name):
            datastore.save_group(group)

def delete_group(group):
    """ Group was deleted. """
    from karaage.machines.models import MachineCategory
    for machine_category in MachineCategory.objects.all():
        name = machine_category.datastore
        for datastore in _get_account_datastores(name):
            datastore.delete_group(group)

def change_group_name(group, old_name, new_name):
    """ Group was renamed. """
    from karaage.machines.models import MachineCategory
    for machine_category in MachineCategory.objects.all():
        name = machine_category.datastore
        for datastore in _get_account_datastores(name):
            datastore.change_group_name(group, old_name, new_name)


def get_group_details(group):
    """ Get group details. """
    result = {}
    from karaage.machines.models import MachineCategory
    for machine_category in MachineCategory.objects.all():
        name = machine_category.datastore
        result[machine_category] = []
        for datastore in _get_account_datastores(name):
            value = datastore.get_group_details(group)
            value['datastore'] = datastore.config['DESCRIPTION']
            result[machine_category].append(value)
    return result

_init_datastores()
