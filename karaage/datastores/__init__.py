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

from django.conf import settings

module = __import__(settings.PERSONAL_DATASTORE, {}, {}, [''])

pds = module.PersonalDataStore()


def activate_user(person):
    pds.activate_user(person)


def delete_user(person):
    pds.delete_user(person)


def update_user(person):
    pds.update_user(person)


def lock_user(person):
    pds.lock_user(person)


def unlock_user(person):
    pds.unlock_user(person)


def set_password(person, raw_password):
    pds.set_password(person, raw_password)


def user_exists(username):
    pds.user_exists(username)


def create_password_hash(raw_password):
    return pds.create_password_hash(raw_password)


def change_username(person, new_username):
    return pds.change_username(person, new_username)


def create_account(person, default_project, machine_category):
    ads_module = __import__(machine_category.datastore, {}, {}, [''])
    ads = ads_module.AccountDataStore(machine_category)
    return ads.create_account(person, default_project)


def delete_account(ua):
    ads_module = __import__(ua.machine_category.datastore, {}, {}, [''])
    ads = ads_module.AccountDataStore(ua.machine_category)
    ads.delete_account(ua)


def update_account(ua):
    ads_module = __import__(ua.machine_category.datastore, {}, {}, [''])

    ads = ads_module.AccountDataStore(ua.machine_category)
    ads.update_account(ua)


def lock_account(ua):
    ads_module = __import__(ua.machine_category.datastore, {}, {}, [''])

    ads = ads_module.AccountDataStore(ua.machine_category)
    ads.lock_account(ua)


def unlock_account(ua):
    ads_module = __import__(ua.machine_category.datastore, {}, {}, [''])

    ads = ads_module.AccountDataStore(ua.machine_category)
    ads.unlock_account(ua)


def change_shell(ua, shell):
    ads_module = __import__(ua.machine_category.datastore, {}, {}, [''])

    ads = ads_module.AccountDataStore(ua.machine_category)
    ads.change_shell(ua, shell)
