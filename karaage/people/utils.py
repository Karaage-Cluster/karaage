# Copyright 2011, 2013-2015 VPAC
# Copyright 2014 The University of Melbourne
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

import re
import six

from django.conf import settings

from karaage.people.models import Person
from karaage.datastores import global_person_exists
from karaage.datastores import machine_category_account_exists
from karaage.machines.models import MachineCategory, Account

username_re = re.compile(r'^%s$' % settings.USERNAME_VALIDATION_RE)


class UsernameException(Exception):
    pass


class UsernameInvalid(UsernameException):
    pass


class UsernameTaken(UsernameException):
    pass


def validate_username(username):
    """ Validate the new username. If the username is invalid, raises
    :py:exc:`UsernameInvalid`.

    :param username: Username to validate.
    """

    # Check username looks ok

    if not username.islower():
        raise UsernameInvalid(six.u('Username must be all lowercase'))
    if len(username) < 2:
        raise UsernameInvalid(six.u('Username must be at least 2 characters'))
    if not username_re.search(username):
        raise UsernameInvalid(settings.USERNAME_VALIDATION_ERROR_MSG)

    return username


def validate_username_for_new_person(username):
    """ Validate the new username for a new person. If the username is invalid
    or in use, raises :py:exc:`UsernameInvalid` or :py:exc:`UsernameTaken`.

    :param username: Username to validate.
    """

    # is the username valid?

    validate_username(username)

    # Check for existing people

    count = Person.objects.filter(username__exact=username).count()
    if count >= 1:
        raise UsernameTaken(six.u(
            'The username is already taken. Please choose another. '
            'If this was the name of your old account please email %s')
            % settings.ACCOUNTS_EMAIL)

    # Check for existing accounts

    count = Account.objects.filter(username__exact=username).count()
    if count >= 1:
        raise UsernameTaken(six.u(
            'The username is already taken. Please choose another. '
            'If this was the name of your old account please email %s')
            % settings.ACCOUNTS_EMAIL)

    # Check person datastore, in case username created outside Karaage.

    if global_person_exists(username):
        raise UsernameTaken(
            six.u('Username is already in external personal datastore.'))

    # Check account datastore, in case username created outside Karaage.

    for mc in MachineCategory.objects.all():
        if machine_category_account_exists(username, mc):
            raise UsernameTaken(
                six.u('Username is already in external account datastore.'))

    return username


def validate_username_for_new_account(person, username):
    """ Validate the new username for a new account. If the username is invalid
    or in use, raises :py:exc:`UsernameInvalid` or :py:exc:`UsernameTaken`.

    :param person: Owner of new account.
    :param username: Username to validate.
    """

    # This is much the same as validate_username_for_new_person, except
    # we don't care if the username is used by the person owning the account

    # is the username valid?

    validate_username(username)

    # Check for existing people

    query = Person.objects.filter(username__exact=username)
    count = query.exclude(pk=person.pk).count()
    if count >= 1:
        raise UsernameTaken(six.u(
            'The username is already taken. Please choose another. '
            'If this was the name of your old account please email %s')
            % settings.ACCOUNTS_EMAIL)

    # Check for existing accounts not belonging to this person

    query = Account.objects.filter(username__exact=username)
    count = query.exclude(person__pk=person.pk).count()
    if count >= 1:
        raise UsernameTaken(six.u(
            'The username is already taken. Please choose another. '
            'If this was the name of your old account please email %s')
            % settings.ACCOUNTS_EMAIL)

    # Check person datastore, in case username created outside Karaage.
    # Make sure we don't count the entry for person.

    query = Person.objects.filter(username__exact=username)
    count = query.filter(pk=person.pk).count()
    if count == 0 and global_person_exists(username):
        raise UsernameTaken(
            six.u('Username is already in external personal datastore.'))


def check_username_for_new_account(person, username, machine_category):
    """ Check the new username for a new account. If the username  is
    in use, raises :py:exc:`UsernameTaken`.

    :param person: Owner of new account.
    :param username: Username to validate.
    :param machine_category: Machine category for new account.
    """

    query = Account.objects.filter(
        username__exact=username,
        machine_category=machine_category,
        date_deleted__isnull=True)

    if query.count() > 0:
        raise UsernameTaken(
            six.u('Username already in use on machine category %s.')
            % machine_category)

    if machine_category_account_exists(username, machine_category):
        raise UsernameTaken(
            six.u('Username is already in datastore for machine category %s.')
            % machine_category)

    return username


def validate_username_for_rename_person(username, person):
    """ Validate the new username to rename a person. If the username is
    invalid or in use, raises :py:exc:`UsernameInvalid` or
    :py:exc:`UsernameTaken`.

    :param username: Username to validate.
    :param person: We exclude this person when checking for duplicates.
    """

    # is the username valid?

    validate_username(username)

    # Check for existing people

    count = Person.objects.filter(username__exact=username) \
        .exclude(pk=person.pk).count()
    if count >= 1:
        raise UsernameTaken(
            six.u('The username is already taken by an existing person.'))

    # Check for existing accounts not owned by person.
    # If there is a conflicting account owned by person it doesn't matter.

    count = Account.objects.filter(username__exact=username) \
        .exclude(person=person).count()
    if count >= 1:
        raise UsernameTaken(
            six.u('The username is already taken by an existing account.'))

    # Check person datastore, in case username created outside Karaage.

    if global_person_exists(username):
        raise UsernameTaken(
            six.u('Username is already in external personal datastore.'))

    # Check account datastore, in case username created outside Karaage.

    for mc in MachineCategory.objects.all():
        # If there is an active account on this MC and we own it, it doesn't
        # matter
        count = Account.objects.filter(
            username__exact=username,
            person=person,
            machine_category=mc,
            date_deleted__isnull=True).count()
        if count == 0 and machine_category_account_exists(username, mc):
            raise UsernameTaken(
                six.u('Username is already in external account datastore.'))
