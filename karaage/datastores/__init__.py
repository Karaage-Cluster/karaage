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
    mc_query = MachineCategory.objects.all().values('datastore').distinct()
    for machine_category in mc_query:
        yield machine_category['datastore']

def get_test_datastore(name=None, number=None):
    """ For testing only. Do not use. """
    if name is None:
        name = settings.LDAP_TEST_DATASTORE
    if number is None:
        number = settings.LDAP_TEST_DATASTORE_N
    datastores = _get_datastores_for_name(name)
    return datastores[number]

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

def add_person_to_group(person, group):
    """ Add person to group. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.add_person_to_group(person, group)

def remove_person_from_group(person, group):
    """ Remove person from group. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.remove_person_from_group(person, group)

def add_person_to_project(person, project):
    """ Add person to project. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.add_person_to_project(person, project)

def remove_person_from_project(person, project):
    """ Remove person from project. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.remove_person_from_project(person, project)

def add_person_to_institute(person, institute):
    """ Add person to institute. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.add_person_to_institute(person, institute)

def remove_person_from_institute(person, institute):
    """ Remove person from institute. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.remove_person_from_institute(person, institute)

def add_person_to_software(person, software):
    """ Add person to software. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.add_person_to_software(person, software)

def remove_person_from_software(person, software):
    """ Remove person from software. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.remove_person_from_software(person, software)

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

def account_edit_form(account):
    """Return the form used to edit the account."""
    name = account.machine_category.datastore
    for datastore in _get_datastores_for_name(name):
        return datastore.edit_form(account)

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

def add_account_to_project(account, project):
    """ Add account to project. """
    name = account.machine_category.datastore
    for datastore in _get_datastores_for_name(name):
        datastore.add_account_to_project(account, project)

def remove_account_from_project(account, project):
    """ Remove account from project. """
    name = account.machine_category.datastore
    for datastore in _get_datastores_for_name(name):
        datastore.remove_account_from_project(account, project)

def add_account_to_institute(account, institute):
    """ Add account to institute. """
    name = account.machine_category.datastore
    for datastore in _get_datastores_for_name(name):
        datastore.add_account_to_institute(account, institute)

def remove_account_from_institute(account, institute):
    """ Remove account from institute. """
    name = account.machine_category.datastore
    for datastore in _get_datastores_for_name(name):
        datastore.remove_account_from_institute(account, institute)

def add_account_to_software(account, software):
    """ Add account to software. """
    name = account.machine_category.datastore
    for datastore in _get_datastores_for_name(name):
        datastore.add_account_to_software(account, software)

def remove_account_from_software(account, software):
    """ Remove account from software. """
    name = account.machine_category.datastore
    for datastore in _get_datastores_for_name(name):
        datastore.remove_account_from_software(account, software)

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

def save_project(project):
    """ An institute has been saved. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.save_project(project)

def delete_project(project):
    """ An institute has been deleted. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.delete_project(project)

def get_project_details(project):
    """ Get details for this user. """
    result = {}
    for name in _get_all_names():
        result[name] = []
        for datastore in _get_datastores_for_name(name):
            value = datastore.get_project_details(project)
            value['datastore'] = datastore.config['DESCRIPTION']
            result[name].append(value)
    return result


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

def get_institute_details(institute):
    """ Get details for this user. """
    result = {}
    for name in _get_all_names():
        result[name] = []
        for datastore in _get_datastores_for_name(name):
            value = datastore.get_institute_details(institute)
            value['datastore'] = datastore.config['DESCRIPTION']
            result[name].append(value)
    return result


############
# Software #
############

def save_software(software):
    """ An institute has been saved. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.save_software(software)

def delete_software(software):
    """ An institute has been deleted. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            datastore.delete_software(software)

def get_software_details(software):
    """ Get details for this user. """
    result = {}
    for name in _get_all_names():
        result[name] = []
        for datastore in _get_datastores_for_name(name):
            value = datastore.get_software_details(software)
            value['datastore'] = datastore.config['DESCRIPTION']
            result[name].append(value)
    return result

###################
# MachineCategory #
###################

def set_mc_datastore(machine_category, old_datastore, new_datastore):
    from karaage.people.models import Person, Group
    from karaage.machines.models import Account, MachineCategory

    mc_query = None
    if new_datastore is not None:
        mc_query = MachineCategory.objects
        mc_query = mc_query.filter(datastore=new_datastore)
        mc_query = mc_query.exclude(pk=machine_category.pk)
        other_mc_refer_datastore = (mc_query.count() > 0)
        for datastore in _get_datastores_for_name(new_datastore):
            if not other_mc_refer_datastore:
                for group in Group.objects.all():
                    datastore.save_group(group)
                for person in Person.objects.all():
                    datastore.save_person(person)
            for account in Account.objects.filter(
                    date_deleted__isnull=True, machine_category=machine_category):
                datastore.save_account(account)
