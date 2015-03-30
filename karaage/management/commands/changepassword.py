# Copyright 2013-2015 VPAC
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

import getpass

from django.core.management.base import BaseCommand, CommandError

from karaage.people.models import Person


class Command(BaseCommand):
    help = "Change a person's password for Karaage."

    def _get_pass(self, prompt="Password: "):
        p = getpass.getpass(prompt=prompt)
        if not p:
            raise CommandError("aborted")
        return p

    def handle(self, *args, **options):
        if len(args) > 1:
            raise CommandError(
                "need exactly one or zero arguments for username")

        if args:
            username, = args
        else:
            username = getpass.getuser()

        try:
            person = Person.objects.get(username=username)
        except Person.DoesNotExist:
            raise CommandError("person '%s' does not exist" % username)

        self.stdout.write("Changing password for person '%s'\n" % person)

        max_tries = 3
        count = 0
        p1, p2 = 1, 2  # To make them initially mismatch.
        while p1 != p2 and count < max_tries:
            p1 = self._get_pass()
            p2 = self._get_pass("Password (again): ")
            if p1 != p2:
                self.stdout.write(
                    "Passwords do not match. Please try again.\n")
                count = count + 1

        if count == max_tries:
            raise CommandError(
                "Aborting password change for user '%s' after %s attempts"
                % (username, count))

        person.set_password(p1)
        person.save()

        return "Password changed successfully for user '%s'" % person
