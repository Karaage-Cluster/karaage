# Copyright 2018 Brian May
#
# This file is part of python-tldap.
#
# python-tldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-tldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-tldap  If not, see <http://www.gnu.org/licenses/>.
""" Various helper functions to aid applications processing schema specific functions. """

import base64
import datetime
from hashlib import sha1
from typing import Dict, List, Optional, Set

import tldap.exceptions
import tldap.fields
import tldap.ldap_passwd as ldap_passwd
from tldap.database import (
    Changeset,
    Database,
    LdapObject,
    LdapObjectClass,
    NotLoadedList,
    NotLoadedObject,
)
from tldap.dn import dn2str, str2dn


def rdn_to_dn(changes: Changeset, name: str, base_dn: str) -> Changeset:
    """ Convert the rdn to a fully qualified DN for the specified LDAP
    connection.

    :param changes: The changes object to lookup.
    :param name: rdn to convert.
    :param base_dn: The base_dn to lookup.
    :return: fully qualified DN.
    """
    dn = changes.get_value_as_single('dn')
    if dn is not None:
        return changes

    value = changes.get_value_as_single(name)
    if value is None:
        raise tldap.exceptions.ValidationError(
            "Cannot use %s in dn as it is None" % name)
    if isinstance(value, list):
        raise tldap.exceptions.ValidationError(
            "Cannot use %s in dn as it is a list" % name)

    assert base_dn is not None

    split_base = str2dn(base_dn)
    split_new_dn = [[(name, value, 1)]] + split_base

    new_dn = dn2str(split_new_dn)

    return changes.set('dn', new_dn)


def set_object_class(changes: Changeset, object_class: List[str]) -> Changeset:
    if len(changes.get_value_as_list('objectClass')) == 0:
        changes = changes.set('objectClass', object_class)
    return changes


# PERSON

def get_fields_person() -> Dict[str, tldap.fields.Field]:
    fields = {
        'cn': tldap.fields.CharField(required=True),
        'displayName': tldap.fields.CharField(required=True),
        'givenName': tldap.fields.CharField(),
        'mail': tldap.fields.CharField(),
        'sn': tldap.fields.CharField(required=True),
        'telephoneNumber': tldap.fields.CharField(),
        'title': tldap.fields.CharField(),
        'uid': tldap.fields.CharField(),
        'userPassword': tldap.fields.CharField(),
        'password': tldap.fields.FakeField(),
        'locked': tldap.fields.FakeField(),
        'groups': tldap.fields.FakeField(max_instances=None),
    }
    return fields


def load_person(python_data: LdapObject, group_table: LdapObjectClass) -> LdapObject:
    python_data = python_data.merge({
        'password': None,
        'groups': NotLoadedList(table=group_table, key="memberUid", value=python_data.get_as_single("uid"))
    })
    return python_data


def save_person(changes: Changeset, database: Database, format_fields: Optional[Set[str]] = None) -> Changeset:
    settings = database.settings

    d = dict()

    if 'password' in changes:
        password = changes.get_value_as_single('password')
        d["userPassword"] = ldap_passwd.encode_password(password)

    if 'groups' in changes:
        groups = changes.get_value_as_list('groups')
        if len(groups) > 0:
            raise RuntimeError("Cannot register changes in groups on people.")

    if 'primary_group' in changes:
        group = changes.get_value_as_single('primary_group')
        assert group.get_as_single('gidNumber') is not None
        d['gidNumber'] = group.get_as_single('gidNumber')

    if format_fields is None:
        format_fields = {'cn'}

    if any(name in changes for name in format_fields):
        values = {
            name: changes.get_value_as_single(name)
            for name in format_fields
        }

        spec = settings.get('DISPLAY_NAME_FORMAT', "{cn}")
        d['displayName'] = spec.format(**values)

    return changes.merge(d)


def get_fields_common() -> Dict[str, tldap.fields.Field]:
    fields = {
        'dn': tldap.fields.FakeField(required=True, max_instances=1),
        'objectClass': tldap.fields.CharField(required=True, max_instances=None),
    }
    return fields


# ACCOUNT

def get_fields_account() -> Dict[str, tldap.fields.Field]:
    fields = {
        'gecos': tldap.fields.CharField(),
        'loginShell': tldap.fields.CharField(),
        'homeDirectory': tldap.fields.CharField(),
        'o': tldap.fields.CharField(),
        'gidNumber': tldap.fields.IntegerField(required=True),
        'uidNumber': tldap.fields.IntegerField(),
        'primary_group': tldap.fields.FakeField(),
    }
    return fields


def load_account(python_data: LdapObject, group_table: LdapObjectClass) -> LdapObject:
    d = {
        'locked': python_data.get_as_single('loginShell').startswith("/locked"),
    }

    if 'gidNumber' in python_data:
        d['primary_group'] = NotLoadedObject(
            table=group_table, key='gidNumber', value=python_data.get_as_single('gidNumber'))

    python_data = python_data.merge(d)
    return python_data


def save_account(changes: Changeset, database: Database, format_fields: Optional[Set[str]] = None) -> Changeset:
    d = {}
    settings = database.settings

    if changes.get_value_as_single('locked') is None:
        d['locked'] = False

    if changes.get_value_as_single('loginShell') is None:
        d['loginShell'] = '/bin/bash'

    changes = changes.merge(d)

    d = {}
    if 'locked' in changes or 'loginShell' in changes:
        locked = changes.get_value_as_single('locked')
        login_shell = changes.get_value_as_single('loginShell')

        if locked is None:
            pass
        elif locked and login_shell is not None:
            if not login_shell.startswith("/locked"):
                d['loginShell'] = '/locked' + login_shell
        elif login_shell is not None:
            if login_shell.startswith("/locked"):
                d['loginShell'] = login_shell[7:]

    if 'primary_group' in changes:
        group = changes.get_value_as_single('primary_group')
        assert group.get_as_single('gidNumber') is not None
        d['gidNumber'] = group.get_as_single('gidNumber')

    if format_fields is None:
        format_fields = {'uid', 'givenName', 'sn', 'o'}

    if any(name in changes for name in format_fields):
        values = {
            name: changes.get_value_as_single(name)
            for name in format_fields
        }

        spec = settings.get('GECOS_FORMAT', "{givenName} {sn}")
        d['gecos'] = spec.format(**values)

        spec = settings.get('HOME_DIRECTORY_FORMAT', "/home/{uid}")
        d['homeDirectory'] = spec.format(**values)

    changes = changes.merge(d)
    return changes


# SHADOW

def get_fields_shadow() -> Dict[str, tldap.fields.Field]:
    fields = {
        'shadowLastChange': tldap.fields.DaysSinceEpochField()
    }
    return fields


def load_shadow(python_data: LdapObject) -> LdapObject:
    return python_data


def save_shadow(changes: Changeset) -> Changeset:
    if 'password' in changes:
        changes = changes.merge({
            'shadowLastChange': datetime.datetime.now().date()
        })
    return changes


# GROUP

def get_fields_group() -> Dict[str, tldap.fields.Field]:
    fields = {
        'cn': tldap.fields.CharField(),
        'description': tldap.fields.CharField(),
        'gidNumber': tldap.fields.IntegerField(),
        'memberUid': tldap.fields.CharField(max_instances=None),
        'members': tldap.fields.FakeField(max_instances=None),
    }
    return fields


def load_group(python_data: LdapObject, account_table: LdapObjectClass) -> LdapObject:
    d = {}

    if 'gidNumber' in python_data:
        d['members'] = [
            NotLoadedObject(table=account_table, key='uid', value=uid)
            for uid in python_data.get_as_list('memberUid')
        ]

    return python_data.merge(d)


def save_group(changes: Changeset) -> Changeset:
    d = {}

    changes = changes.merge(d)

    d = {}

    if 'cn' in changes:
        cn = changes.get_value_as_single('cn')
        description = changes.get_value_as_single('description')
        if description is None:
            d['description'] = cn

    if 'members' in changes:
        members = changes.get_value_as_list('members')
        d['memberUid'] = [v.get_as_single('uid') for v in members]

    return changes.merge(d)


def add_group_member(changes: Changeset, member: LdapObject) -> Changeset:
    add_uid = member.get_as_single('uid')
    member_uid = changes.get_value_as_list('memberUid')
    if add_uid not in member_uid:
        changes = changes.force_add('memberUid', [add_uid])
    return changes


def remove_group_member(changes: Changeset, member: LdapObject) -> Changeset:
    rm_uid = member.get_as_single('uid')
    member_uid = changes.get_value_as_list('memberUid')
    if rm_uid in member_uid:
        changes = changes.force_delete('memberUid', [rm_uid])
    return changes


# PWDPOLICY

def get_fields_pwdpolicy() -> Dict[str, tldap.fields.Field]:
    fields = {
        'pwdAttribute': tldap.fields.CharField(),
        'pwdAccountLockedTime': tldap.fields.CharField(max_instances=None),
    }
    return fields


def load_pwdpolicy(python_data: LdapObject) -> LdapObject:
    python_data = python_data.merge({
        'locked': len(python_data['pwdAccountLockedTime']) > 0,
    })
    return python_data


def save_pwdpolicy(changes: Changeset) -> Changeset:
    d = {}

    if changes.get_value_as_single('locked') is None:
        d['locked'] = False

    changes = changes.merge(d)

    d = {}

    pwd_attribute = changes.get_value_as_single('pwdAttribute')
    if pwd_attribute is None:
        d['pwdAttribute'] = 'userPassword'

    if 'locked' in changes:
        locked = changes.get_value_as_single('locked')
        if locked:
            d['pwdAccountLockedTime'] = ['000001010000Z']
        else:
            d['pwdAccountLockedTime'] = []

    changes = changes.merge(d)
    return changes


# PASSWORD_OBJECT - ds389

def get_fields_password_object() -> Dict[str, tldap.fields.Field]:
    fields = {
        'nsAccountLock': tldap.fields.CharField(),
    }
    return fields


def load_password_object(python_data: LdapObject) -> LdapObject:
    def is_locked():
        account_lock = python_data.get_as_single('nsAccountLock')
        if account_lock is None:
            return False
        else:
            return account_lock.lower() == 'true'

    python_data = python_data.merge({
        'locked': is_locked()
    })
    return python_data


def save_password_object(changes: Changeset) -> Changeset:
    d = {}

    if changes.get_value_as_single('locked') is None:
        d['locked'] = False

    changes = changes.merge(d)

    d = {}

    if 'locked' in changes:
        locked = changes.get_value_as_single('locked')
        if locked:
            d['nsAccountLock'] = "TRUE"
        else:
            d['nsAccountLock'] = None

    changes = changes.merge(d)
    return changes


# SHIBBOLETH

def get_fields_shibboleth() -> Dict[str, tldap.fields.Field]:
    fields = {
        'auEduPersonSharedToken': tldap.fields.CharField(),
        'eduPersonAffiliation': tldap.fields.CharField(),
    }
    return fields


def load_shibboleth(python_data: LdapObject) -> LdapObject:
    return python_data


def save_shibboleth(changes: Changeset, database: Database) -> Changeset:
    d = {}
    settings = database.settings

    if 'uid' in changes:
        uid = changes.get_value_as_single('uid')
        token = changes.get_value_as_single('auEduPersonSharedToken')
        if token is None:
            entity_id = settings['SHIBBOLETH_URL']
            salt = settings['SHIBBOLETH_SALT']
            token = base64.urlsafe_b64encode(sha1(uid + entity_id + salt).digest())[:-1]
            d['auEduPersonSharedToken'] = token

    if 'locked' in changes:
        locked = changes.get_value_as_single('locked')
        if locked:
            d['eduPersonAffiliation'] = 'affiliate'
        else:
            d['eduPersonAffiliation'] = 'staff'

    changes = changes.merge(d)
    return changes
