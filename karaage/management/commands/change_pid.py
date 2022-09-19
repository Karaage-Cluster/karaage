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

import re
import sys

import django.db.transaction
import tldap.transaction
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from karaage.projects.models import Project


try:
    input = raw_input
except NameError:
    pass


class Command(BaseCommand):
    help = "Change a pid for a project and all accounts for that project"

    def add_arguments(self, parser):
        parser.add_argument("old_pid", type=str)
        parser.add_argument("new_pid", type=str)

    @django.db.transaction.atomic
    @tldap.transaction.commit_on_success
    def handle(self, *args, **options):
        old = options["old_pid"]
        new = options["new_pid"]

        try:
            project = Project.objects.get(pid=old)
        except Project.DoesNotExist:
            raise CommandError("project %s does not exist" % old)

        project_re = re.compile(r"^%s$" % settings.PROJECT_VALIDATION_RE)
        if not project_re.search(new):
            raise CommandError(settings.PROJECT_VALIDATION_ERROR_MSG)

        while True:
            confirm = input('Change project "%s" to "%s (yes,no): ' % (old, new))
            if confirm == "yes":
                break
            elif confirm == "no":
                return sys.exit(0)
            else:
                print("Please enter yes or no")

        project.pid = new
        project.save()
        print("Changed pid on project")

        print("Done")
