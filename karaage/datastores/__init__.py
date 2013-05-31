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
    return pds.user_exists(username)


def change_username(person, new_username):
    pds.change_username(person, new_username)


def create_account(ua):
    ads_module = __import__(ua.machine_category.datastore, {}, {}, [''])
    ads = ads_module.AccountDataStore()
    ads.create_account(ua)


def delete_account(ua):
    ads_module = __import__(ua.machine_category.datastore, {}, {}, [''])
    ads = ads_module.AccountDataStore()
    ads.delete_account(ua)


def update_account(ua):
    ads_module = __import__(ua.machine_category.datastore, {}, {}, [''])
    ads = ads_module.AccountDataStore()
    ads.update_account(ua)


def lock_account(ua):
    ads_module = __import__(ua.machine_category.datastore, {}, {}, [''])
    ads = ads_module.AccountDataStore()
    ads.lock_account(ua)


def unlock_account(ua):
    ads_module = __import__(ua.machine_category.datastore, {}, {}, [''])
    ads = ads_module.AccountDataStore()
    ads.unlock_account(ua)


def change_shell(ua, shell):
    ads_module = __import__(ua.machine_category.datastore, {}, {}, [''])
    ads = ads_module.AccountDataStore()
    ads.change_shell(ua, shell)


def set_account_password(ua, raw_password):
    ads_module = __import__(ua.machine_category.datastore, {}, {}, [''])
    ads = ads_module.AccountDataStore()
    ads.set_password(ua, raw_password)


def account_exists(username, machine_category):
    ads_module = __import__(machine_category.datastore, {}, {}, [''])
    ads = ads_module.AccountDataStore()
    return ads.account_exists(username)


def change_account_username(ua, new_username):
    ads_module = __import__(ua.machine_category.datastore, {}, {}, [''])
    ads = ads_module.AccountDataStore()
    ads.change_username(ua, new_username)
