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

""" LDAP datastore. """

import importlib
import logging

import tldap.backend
from tldap import Q
from tldap.database import (
    Database,
    LdapObject,
    LdapObjectClass,
    changeset,
    delete,
    get_one,
    preload,
    rename,
    save,
)
from tldap.exceptions import ObjectDoesNotExist

import karaage.common.trace as trace
from karaage.datastores import base
from karaage.datastores.ldap_schemas import OpenldapAccount, OpenldapGroup
from karaage.machines.models import Account


logger = logging.getLogger(__name__)


def _str_or_none(string):
    """Return a string of None if string is empty."""
    if string is None or string == "":
        return None
    return string


def _lookup(cls: str) -> LdapObjectClass:
    """Lookup module.class."""
    if isinstance(cls, str):
        module_name, _, name = cls.rpartition(".")
        module = importlib.import_module(module_name)
        try:
            cls = getattr(module, name)
        except AttributeError:
            raise AttributeError("%s reference cannot be found" % cls)
    return cls


class DataStore(base.DataStore):
    """LDAP Account and group datastore."""

    def __init__(self, config: dict) -> None:
        super(DataStore, self).__init__(config)
        using = config["LDAP"]

        connection = tldap.backend.connections[using]
        self._database = Database(connection, config)

        self._account_class = _lookup(config["ACCOUNT"])
        self._group_class = _lookup(config["GROUP"])
        self._primary_group = config.get("PRIMARY_GROUP", "institute")
        self._default_primary_group = config.get("DEFAULT_PRIMARY_GROUP", "dummy")
        self._settings = config

    def _get_account(self, uid: str) -> LdapObject:
        return get_one(
            table=self._account_class,
            query=Q(uid=uid),
            database=self._database,
        )

    def _get_group(self, cn: str) -> LdapObject:
        return get_one(
            table=self._group_class,
            query=Q(cn=cn),
            database=self._database,
        )

    def save_account(self, account: Account) -> None:
        """Account was saved."""
        person = account.person
        if self._primary_group == "institute":
            lgroup = self._get_group(person.institute.group.name)
        elif self._primary_group == "default_project":
            if account.default_project is None:
                lgroup = self._get_group(self._default_primary_group)
            else:
                lgroup = self._get_group(account.default_project.group.name)
        else:
            raise RuntimeError("Unknown value of PRIMARY_GROUP.")

        if account.default_project is None:
            default_project = "none"
        else:
            default_project = account.default_project.pid

        try:
            luser = self._get_account(account.username)
            changes = changeset(luser, {})
            new_user = False
        except ObjectDoesNotExist:
            new_user = True
            luser = self._account_class()
            changes = changeset(luser, {"uid": account.username})

        changes = changes.merge(
            {
                "gidNumber": lgroup["gidNumber"],
                "givenName": person.first_name,
                "sn": person.last_name,
                "telephoneNumber": _str_or_none(person.telephone),
                "mail": _str_or_none(person.email),
                "title": _str_or_none(person.title),
                "o": person.institute.name,
                "cn": person.full_name,
                "default_project": default_project,
                "loginShell": account.shell,
                "locked": account.is_locked(),
            }
        )
        save(changes, database=self._database)

        if new_user:
            # add all groups
            for group in account.person.groups.all():
                self.add_account_to_group(account, group)

    def delete_account(self, account):
        """Account was deleted."""
        try:
            luser = self._get_account(account.username)
            groups = luser["groups"].load(database=self._database)
            for group in groups:
                changes = changeset(group, {})
                changes = group.remove_member(changes, luser)
                save(changes, database=self._database)

            delete(luser, database=self._database)
        except ObjectDoesNotExist:
            # it doesn't matter if it doesn't exist
            pass

    def set_account_password(self, account, raw_password):
        """Account's password was changed."""
        luser = self._get_account(account.username)
        changes = changeset(
            luser,
            {
                "password": raw_password,
            },
        )
        save(changes, database=self._database)

    def set_account_username(self, account, old_username, new_username):
        """Account's username was changed."""
        luser = self._get_account(old_username)
        rename(luser, database=self._database, uid=new_username)

    def add_account_to_group(self, account, group):
        """Add account to group."""
        lgroup: OpenldapGroup = self._get_group(group.name)
        person: OpenldapAccount = self._get_account(account.username)

        changes = changeset(lgroup, {})
        changes = lgroup.add_member(changes, person)
        save(changes, database=self._database)

    def remove_account_from_group(self, account, group):
        """Remove account from group."""
        lgroup: OpenldapGroup = self._get_group(group.name)
        person: OpenldapAccount = self._get_account(account.username)

        changes = changeset(lgroup, {})
        changes = lgroup.remove_member(changes, person)
        save(changes, database=self._database)

    def get_account_details(self, account):
        """Get the account details."""
        result = {}
        try:
            luser = self._get_account(account.username)
            luser = preload(luser, database=self._database)
        except ObjectDoesNotExist:
            return result

        for i, j in luser.items():
            if i != "userPassword" and j is not None:
                result[i] = j

        return result

    def account_exists(self, username):
        """Does the account exist?"""
        try:
            self._get_account(username)
            return True
        except ObjectDoesNotExist:
            return False

    def save_group(self, group):
        """Group was saved."""
        # If group already exists, take over existing group rather then error.
        try:
            lgroup = self._get_group(group.name)
            changes = changeset(lgroup, {})
        except ObjectDoesNotExist:
            lgroup = self._group_class()
            changes = changeset(
                lgroup,
                {
                    "cn": group.name,
                },
            )

        changes = changes.merge({"description": group.description})
        save(changes, database=self._database)

    def delete_group(self, group):
        """Group was deleted."""
        try:
            lgroup = self._get_group(group.name)
            delete(lgroup, database=self._database)
        except ObjectDoesNotExist:
            # it doesn't matter if it doesn't exist
            pass

    def set_group_name(self, group, old_name, new_name):
        """Group was renamed."""
        lgroup = self._get_group(old_name)
        rename(lgroup, database=self._database, cn=new_name)

    def get_group_details(self, group):
        """Get the group details."""
        result = {}
        try:
            lgroup = self._get_group(group.name)
            lgroup = preload(lgroup, database=self._database)
        except ObjectDoesNotExist:
            return result

        for i, j in lgroup.items():
            if j is not None:
                result[i] = j

        return result


trace.attach(trace.trace(logger), DataStore)
