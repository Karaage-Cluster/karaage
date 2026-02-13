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

""" Django specific database helper functions. """

from tldap import Q
from tldap.database import Changeset, Database, LdapObjectClass, get_one
from tldap.django.models import Counters
from tldap.exceptions import ObjectDoesNotExist


def _check_exists(database: Database, table: LdapObjectClass, key: str, value: str):
    """ Check if a given LDAP object exists. """
    try:
        get_one(table, Q(**{key: value}), database=database)
        return True
    except ObjectDoesNotExist:
        return False


def save_account(changes: Changeset, table: LdapObjectClass, database: Database) -> Changeset:
    """ Modify a changes to add an automatically generated uidNumber. """
    d = {}
    settings = database.settings

    uid_number = changes.get_value_as_single('uidNumber')
    if uid_number is None:
        scheme = settings['NUMBER_SCHEME']
        first = settings.get('UID_FIRST', 10000)
        d['uidNumber'] = Counters.get_and_increment(
            scheme, "uidNumber", first,
            lambda n: not _check_exists(database, table, 'uidNumber', n)
        )

    changes = changes.merge(d)
    return changes


def save_group(changes: Changeset, table: LdapObjectClass, database: Database) -> Changeset:
    """ Modify a changes to add an automatically generated gidNumber. """
    d = {}
    settings = database.settings

    gid_number = changes.get_value_as_single('gidNumber')
    if gid_number is None:
        scheme = settings['NUMBER_SCHEME']
        first = settings.get('GID_FIRST', 10000)
        d['gidNumber'] = Counters.get_and_increment(
            scheme, "gidNumber", first,
            lambda n: not _check_exists(database, table, 'gidNumber', n)
        )

    changes = changes.merge(d)
    return changes
