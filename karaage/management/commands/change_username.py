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

import sys

import django.db.transaction
import tldap.transaction
from django.core.management.base import BaseCommand, CommandError

from karaage.people.models import Person
from karaage.people.utils import (
    UsernameInvalid,
    UsernameTaken,
    validate_username_for_rename_person,
)


try:
    input = raw_input
except NameError:
    pass


class Command(BaseCommand):
    help = "Change a username for a person and all accounts for that person"

    def add_arguments(self, parser):
        parser.add_argument("old_username", type=str)
        parser.add_argument("new_username", type=str)

    @django.db.transaction.atomic
    @tldap.transaction.commit_on_success
    def handle(self, *args, **options):
        old = options["old_username"]
        new = options["new_username"]

        try:
            person = Person.objects.get(username=old)
        except Person.DoesNotExist:
            raise CommandError("person %s does not exist" % old)

        try:
            validate_username_for_rename_person(new, person)
        except UsernameInvalid as e:
            raise CommandError(e.args[0])
        except UsernameTaken as e:
            raise CommandError(e.args[0])

        while 1:
            confirm = input('Change person "%s" and accounts to "%s (yes,no): ' % (old, new))
            if confirm == "yes":
                break
            elif confirm == "no":
                return sys.exit(0)
            else:
                print("Please enter yes or no")

        for account in person.account_set.filter(date_deleted__isnull=True):
            account.username = new
            account.save()
            print("Changed username to %s" % account.username)

        person.username = new
        person.save()
        print("Changed username on person")

        print("Done")
