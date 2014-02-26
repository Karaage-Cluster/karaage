# Copyright 2007-2014 VPAC
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

from .base import GlobalDataStore, MachineCategoryDataStore
from karaage.machines.models import MachineCategory

_GLOBAL_DATASTORES = []
_MACHINE_CATEGORY_DATASTORES = {}

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
    array = settings.GLOBAL_DATASTORES
    for config in array:
        cls = _lookup(config['ENGINE'])
        assert issubclass(cls, GlobalDataStore)
        _GLOBAL_DATASTORES.append(cls(config))
    for name, array in settings.MACHINE_CATEGORY_DATASTORES.iteritems():
        _MACHINE_CATEGORY_DATASTORES[name] = []
        for config in array:
            cls = _lookup(config['ENGINE'])
            assert issubclass(cls, MachineCategoryDataStore)
            _MACHINE_CATEGORY_DATASTORES[name].append(cls(config))

def _get_global_datastores():
    return _GLOBAL_DATASTORES

def _get_machine_category_datastores(machine_category):
    """ Get the datastores for machine category. """
    name = machine_category.datastore
    return _MACHINE_CATEGORY_DATASTORES[name]

def _get_machine_categorys():
    return MachineCategory.objects.all()

def get_global_test_datastore(number=None):
    """ For testing only. Do not use. """
    if number is None:
        number = settings.LDAP_TEST_DATASTORE_N
    datastores = _GLOBAL_DATASTORES
    return datastores[number]

def get_machine_category_test_datastore(name=None, number=None):
    """ For testing only. Do not use. """
    if name is None:
        name = settings.LDAP_TEST_DATASTORE
    if number is None:
        number = settings.LDAP_TEST_DATASTORE_N
    datastores = _MACHINE_CATEGORY_DATASTORES[name]
    return datastores[number]

# Initialize data stores
_init_datastores()


######################################################################
# GLOBAL DATA STORES                                                 #
######################################################################


##########
# Person #
##########

def global_save_person(person):
    """ Person was saved. """
    for datastore in _get_global_datastores():
        datastore.save_person(person)

def global_delete_person(person):
    """ Person was deleted. """
    for datastore in _get_global_datastores():
        datastore.delete_person(person)

def global_set_person_password(person, raw_password):
    """ Person's password was changed. """
    for datastore in _get_global_datastores():
        datastore.set_person_password(person, raw_password)

def global_set_person_username(person, old_username, new_username):
    """ Person's username was changed. """
    for datastore in _get_global_datastores():
        datastore.set_person_username(person, old_username, new_username)

def global_add_person_to_group(person, group):
    """ Add person to group. """
    for datastore in _get_global_datastores():
        datastore.add_person_to_group(person, group)

def global_remove_person_from_group(person, group):
    """ Remove person from group. """
    for datastore in _get_global_datastores():
        datastore.remove_person_from_group(person, group)

def global_add_person_to_project(person, project):
    """ Add person to project. """
    for datastore in _get_global_datastores():
        datastore.add_person_to_project(person, project)

def global_remove_person_from_project(person, project):
    """ Remove person from project. """
    for datastore in _get_global_datastores():
        datastore.remove_person_from_project(person, project)

def global_person_exists(username):
    """ Does this person exist??? """
    for datastore in _get_global_datastores():
        if datastore.person_exists(username):
            return True
    return False

def global_get_person_details(person):
    """ Get details for this user. """
    result = []
    for datastore in _get_global_datastores():
        value = datastore.get_person_details(person)
        value['datastore'] = datastore.config['DESCRIPTION']
        result.append(value)
    return result


#########
# Group #
#########

def global_save_group(group):
    """ Group was saved. """
    for datastore in _get_global_datastores():
        datastore.save_group(group)

def global_delete_group(group):
    """ Group was deleted. """
    for datastore in _get_global_datastores():
        datastore.delete_group(group)

def global_set_group_name(group, old_name, new_name):
    """ Group was renamed. """
    for datastore in _get_global_datastores():
        datastore.set_group_name(group, old_name, new_name)

def global_get_group_details(group):
    """ Get group details. """
    result = []
    for datastore in _get_global_datastores():
        value = datastore.get_group_details(group)
        value['datastore'] = datastore.config['DESCRIPTION']
        result.append(value)
    return result


######################################################################
# MACHINE CATEGORY DATASTORES                                        #
######################################################################


###########
# Account #
###########

def machine_category_save_account(account):
    """ Account was saved. """
    for datastore in _get_machine_category_datastores(account.machine_category):
        datastore.save_account(account)

def machine_category_delete_account(account):
    """ Account was deleted. """
    for datastore in _get_machine_category_datastores(account.machine_category):
        datastore.delete_account(account)

def machine_category_set_account_password(account, raw_password):
    """ Account's password was changed. """
    for datastore in _get_machine_category_datastores(account.machine_category):
        datastore.set_account_password(account, raw_password)

def machine_category_set_account_username(account, old_username, new_username):
    """ Account's username was changed. """
    for datastore in _get_machine_category_datastores(account.machine_category):
        datastore.set_account_username(account, old_username, new_username)

def machine_category_add_account_to_group(account, group):
    """ Add account to group. """
    for datastore in _get_machine_category_datastores(account.machine_category):
        datastore.add_account_to_group(account, group)

def machine_category_remove_account_from_group(account, group):
    """ Remove account from group. """
    for datastore in _get_machine_category_datastores(account.machine_category):
        datastore.remove_account_from_group(account, group)

def machine_category_add_account_to_project(account, project):
    """ Add account to project. """
    for datastore in _get_machine_category_datastores(account.machine_category):
        datastore.add_account_to_project(account, project)

def machine_category_remove_account_from_project(account, project):
    """ Remove account from project. """
    for datastore in _get_machine_category_datastores(account.machine_category):
        datastore.remove_account_from_project(account, project)

def machine_category_add_account_to_institute(account, institute):
    """ Add account to institute. """
    for datastore in _get_machine_category_datastores(account.machine_category):
        datastore.add_account_to_institute(account, institute)

def machine_category_remove_account_from_institute(account, institute):
    """ Remove account from institute. """
    for datastore in _get_machine_category_datastores(account.machine_category):
        datastore.remove_account_from_institute(account, institute)

def machine_category_add_account_to_software(account, software):
    """ Add account to software. """
    for datastore in _get_machine_category_datastores(account.machine_category):
        datastore.add_account_to_software(account, software)

def machine_category_remove_account_from_software(account, software):
    """ Remove account from software. """
    for datastore in _get_machine_category_datastores(account.machine_category):
        datastore.remove_account_from_software(account, software)

def machine_category_account_exists(username, machine_category):
    """ Does the account exist??? """
    for datastore in _get_machine_category_datastores(machine_category):
        if datastore.account_exists(username):
            return True
    return False

def machine_category_get_account_details(account):
    """ Get the account details. """
    machine_category = account.machine_category
    result = {}
    result[machine_category.name] = []
    for datastore in _get_machine_category_datastores(machine_category):
        value = datastore.get_account_details(account)
        value['datastore'] = datastore.config['DESCRIPTION']
        result[machine_category.name].append(value)
    return result


#########
# Group #
#########

def machine_category_save_group(group):
    """ Group was saved. """
    for machine_category in _get_machine_categorys():
        for datastore in _get_machine_category_datastores(machine_category):
            datastore.save_group(group)

def machine_category_delete_group(group):
    """ Group was deleted. """
    for machine_category in _get_machine_categorys():
        for datastore in _get_machine_category_datastores(machine_category):
            datastore.delete_group(group)

def machine_category_set_group_name(group, old_name, new_name):
    """ Group was renamed. """
    for machine_category in _get_machine_categorys():
        for datastore in _get_machine_category_datastores(machine_category):
            datastore.set_group_name(group, old_name, new_name)

def machine_category_get_group_details(group):
    """ Get group details. """
    result = {}
    for machine_category in _get_machine_categorys():
        result[machine_category.name] = []
        for datastore in _get_machine_category_datastores(machine_category):
            value = datastore.get_group_details(group)
            value['datastore'] = datastore.config['DESCRIPTION']
            result[machine_category.name].append(value)
    return result


###########
# Project #
###########

def machine_category_save_project(project):
    """ An machine has been saved. """
    for project_quota in project.projectquota_set.all():
        for datastore in _get_machine_category_datastores(project_quota.machine_category):
            datastore.save_project(project)

def machine_category_delete_project(project, machine_category=None):
    """ An machine has been deleted. """
    if machine_category is None:
        for project_quota in project.projectquota_set.all():
            for datastore in _get_machine_category_datastores(project_quota.machine_category):
                datastore.delete_project(project)
    else:
        for datastore in _get_machine_category_datastores(machine_category):
            datastore.delete_project(project)

def machine_category_get_project_details(project):
    """ Get details for this user. """
    result = {}
    for project_quota in project.projectquota_set.all():
        machine_category = project_quota.machine_category
        result[machine_category.name] = []
        for datastore in _get_machine_category_datastores(machine_category):
            value = datastore.get_project_details(project)
            value['datastore'] = datastore.config['DESCRIPTION']
            result[machine_category.name].append(value)
    return result


#############
# Institute #
#############

def machine_category_save_institute(institute):
    """ An institute has been saved. """
    for institute_quota in institute.institutequota_set.all():
        for datastore in _get_machine_category_datastores(institute_quota.machine_category):
            datastore.save_institute(institute)

def machine_category_delete_institute(institute, machine_category):
    """ An institute has been deleted. """
    if machine_category is None:
        for institute_quota in institute.institutequota_set.all():
            for datastore in _get_machine_category_datastores(institute_quota.machine_category):
                datastore.delete_institute(institute)
    else:
        for datastore in _get_machine_category_datastores(machine_category):
            datastore.delete_institute(institute)

def machine_category_get_institute_details(institute):
    """ Get details for this user. """
    result = {}
    for institute_quota in institute.institutequota_set.all():
        machine_category = institute_quota.machine_category
        result[machine_category.name] = []
        for datastore in _get_machine_category_datastores(machine_category):
            value = datastore.get_institute_details(institute)
            value['datastore'] = datastore.config['DESCRIPTION']
            result[machine_category.name].append(value)
    return result


############
# Software #
############

def machine_category_save_software(software):
    """ An institute has been saved. """
    for machine_category in _get_machine_categorys():
        for datastore in _get_machine_category_datastores(machine_category):
            datastore.save_software(software)

def machine_category_delete_software(software):
    """ An institute has been deleted. """
    for machine_category in _get_machine_categorys():
        for datastore in _get_machine_category_datastores(machine_category):
            datastore.delete_software(software)

def machine_category_get_software_details(software):
    """ Get details for this user. """
    result = {}
    for machine_category in _get_machine_categorys():
        result[machine_category.name] = []
        for datastore in _get_machine_category_datastores(machine_category):
            value = datastore.get_software_details(software)
            value['datastore'] = datastore.config['DESCRIPTION']
            result[machine_category.name].append(value)
    return result


######################################################################
# OTHER                                                              #
######################################################################


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
        for datastore in _get_machine_category_datastores(new_datastore):
            if not other_mc_refer_datastore:
                for group in Group.objects.all():
                    datastore.save_group(group)
            for account in Account.objects.filter(
                    date_deleted__isnull=True, machine_category=machine_category):
                datastore.save_account(account)
