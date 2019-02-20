# Copyright 2018, Brian May
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

from typing import Dict

import tldap.django.helpers as dhelpers
import tldap.fields
from tldap.database import (
    Changeset,
    Database,
    LdapObject,
    SearchOptions,
    helpers,
)


class BaseAccount(LdapObject):
    """ An abstract Generic LDAP account. """

    @classmethod
    def get_fields(cls) -> Dict[str, tldap.fields.Field]:
        fields = {
            **helpers.get_fields_common(),
            **helpers.get_fields_person(),
            **helpers.get_fields_account(),
            **helpers.get_fields_shadow(),
            'default_project': tldap.fields.FakeField(required=True),
        }
        return fields

    @classmethod
    def get_search_options(cls, database: Database) -> SearchOptions:
        settings = database.settings
        return SearchOptions(
            base_dn=settings['LDAP_ACCOUNT_BASE'],
            object_class={'inetOrgPerson', 'organizationalPerson', 'person'},
            pk_field="uid",
        )

    @classmethod
    def on_load(cls, python_data: LdapObject, _database: Database) -> LdapObject:
        python_data = helpers.load_person(python_data, OpenldapGroup)
        python_data = helpers.load_account(python_data, OpenldapGroup)
        python_data = helpers.load_shadow(python_data)
        return python_data

    @classmethod
    def on_save(cls, changes: Changeset, database: Database) -> Changeset:
        settings = database.settings
        changes = helpers.save_person(changes, database)
        changes = helpers.save_account(changes, database, {'uid', 'cn', 'givenName', 'sn', 'o', 'default_project'})
        changes = helpers.save_shadow(changes)
        changes = helpers.rdn_to_dn(changes, 'uid', settings['LDAP_ACCOUNT_BASE'])
        return changes

    def __repr__(self):
        return f"user:{self['uid'][0]}"


class BaseGroup(LdapObject):
    """ An abstract generic LDAP Group. """

    @classmethod
    def get_fields(cls) -> Dict[str, tldap.fields.Field]:
        fields = {
            **helpers.get_fields_common(),
            **helpers.get_fields_group(),
        }
        return fields

    @classmethod
    def get_search_options(cls, database: Database) -> SearchOptions:
        settings = database.settings
        return SearchOptions(
            base_dn=settings['LDAP_GROUP_BASE'],
            object_class={'posixGroup'},
            pk_field="cn",
        )

    @classmethod
    def on_load(cls, python_data: LdapObject, _database: Database) -> LdapObject:
        return python_data

    @classmethod
    def on_save(cls, changes: Changeset, database: Database) -> Changeset:
        settings = database.settings
        changes = helpers.save_group(changes)
        changes = helpers.set_object_class(changes, ['top', 'posixGroup'])
        changes = helpers.rdn_to_dn(changes, 'cn', settings['LDAP_GROUP_BASE'])
        return changes

    @classmethod
    def add_member(cls, changes: Changeset, member: BaseAccount) -> Changeset:
        return helpers.add_group_member(changes, member)

    @classmethod
    def remove_member(cls, changes: Changeset, member: BaseAccount) -> Changeset:
        return helpers.remove_group_member(changes, member)

    def __repr__(self):
        return f"group:{self['cn'][0]}"


class OpenldapAccount(BaseAccount):
    """ An OpenLDAP specific account with the pwdpolicy schema. """

    @classmethod
    def get_fields(cls) -> Dict[str, tldap.fields.Field]:
        fields = {
            **BaseAccount.get_fields(),
            **helpers.get_fields_pwdpolicy(),
        }
        return fields

    @classmethod
    def on_load(cls, python_data: LdapObject, database: Database) -> LdapObject:
        python_data = BaseAccount.on_load(python_data, database)
        python_data = helpers.load_pwdpolicy(python_data)
        return python_data

    @classmethod
    def on_save(cls, changes: Changeset, database: Database) -> Changeset:
        changes = BaseAccount.on_save(changes, database)
        changes = dhelpers.save_account(changes, OpenldapAccount, database)
        changes = helpers.save_pwdpolicy(changes)
        changes = helpers.set_object_class(changes, ['top', 'person', 'inetOrgPerson', 'organizationalPerson',
                                                     'shadowAccount', 'posixAccount', 'pwdPolicy'])
        return changes


class OpenldapGroup(BaseGroup):
    """ An OpenLDAP specific group. """

    @classmethod
    def on_load(cls, python_data: LdapObject, database: Database) -> LdapObject:
        python_data = BaseGroup.on_load(python_data, database)
        python_data = helpers.load_group(python_data, OpenldapAccount)
        return python_data

    @classmethod
    def on_save(cls, changes: Changeset, database: Database) -> Changeset:
        changes = BaseGroup.on_save(changes, database)
        changes = dhelpers.save_group(changes, OpenldapGroup, database)
        return changes


class Ds389Account(BaseAccount):
    """ A DS389 specific account with the password object schema. """

    @classmethod
    def get_fields(cls) -> Dict[str, tldap.fields.Field]:
        fields = {
            **BaseAccount.get_fields(),
            **helpers.get_fields_password_object(),
        }
        return fields

    @classmethod
    def on_load(cls, python_data: LdapObject, database: Database) -> LdapObject:
        python_data = BaseAccount.on_load(python_data, database)
        python_data = helpers.load_password_object(python_data)
        return python_data

    @classmethod
    def on_save(cls, changes: Changeset, database: Database) -> Changeset:
        changes = BaseAccount.on_save(changes, database)
        changes = dhelpers.save_account(changes, Ds389Account, database)
        changes = helpers.save_password_object(changes)
        changes = helpers.set_object_class(changes, ['top', 'person', 'inetOrgPerson', 'organizationalPerson',
                                                     'shadowAccount', 'posixAccount', 'passwordObject'])
        return changes


class Ds389Group(BaseGroup):
    """ A DS389 specific group. """

    @classmethod
    def on_load(cls, python_data: LdapObject, database: Database) -> LdapObject:
        python_data = BaseGroup.on_load(python_data, database)
        python_data = helpers.load_group(python_data, Ds389Account)
        return python_data

    @classmethod
    def on_save(cls, changes: Changeset, database: Database) -> Changeset:
        changes = BaseGroup.on_save(changes, database)
        changes = dhelpers.save_group(changes, Ds389Group, database)
        return changes
