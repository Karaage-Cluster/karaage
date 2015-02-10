# Copyright 2010, 2013-2015 VPAC
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

"""
Management utility to import user from a CSV file.

CSV format should be:

username,password,short_name,full_name,email,institute,project
sam,secret,Joe,Joe Bloggs,joe@example.com,Test,TestProject2
bob,secret2,Bob,Bob Smith,bob@example.com,Example University,pEx0032


"""

import re
import sys
from csv import DictReader
from django.core import exceptions
from django.core.management.base import BaseCommand
from django.core.validators import validate_email

from karaage.people.models import Person
from karaage.institutes.models import Institute
from karaage.projects.models import Project
from karaage.projects.utils import add_user_to_project

import django.db.transaction
import tldap.transaction

RE_VALID_USERNAME = re.compile('[\w.@+-]+$')


class Command(BaseCommand):
    help = """Import users from a CSV file with the following format.
username,password,short_name,full_name,email,institute,project"""
    args = "csvfile"

    @django.db.transaction.atomic
    @tldap.transaction.commit_on_success
    def handle(self, csvfile, **options):
        verbosity = int(options.get('verbosity', 1))

        try:
            data = DictReader(open(csvfile))
        except:
            sys.stderr.write("ERROR: Failed to read CSV file.\n")
            sys.exit(1)

        success = 0
        fail_count = 0
        skip = 0
        for user in data:
            fail = False

            if verbosity >= 1:
                print("Attempting to import user '%s'" % user['username'])

            if 'username' not in user:
                sys.stderr.write("Error: Failed to find username column.\n")
                fail = True
            if 'password' not in user:
                sys.stderr.write("Error: Failed to find password column.\n")
                fail = True
            if 'short_name' not in user:
                sys.stderr.write("Error: Failed to find short_name column.\n")
                fail = True
            if 'full_name' not in user:
                sys.stderr.write("Error: Failed to find full_name column.\n")
                fail = True
            if 'email' not in user:
                sys.stderr.write("Error: Failed to find email column.\n")
                fail = True
            if 'institute' not in user:
                sys.stderr.write("Error: Failed to find institute column.\n")
                fail = True
            if 'project' not in user:
                sys.stderr.write("Error: Failed to find project column.\n")
                fail = True

            if not RE_VALID_USERNAME.match(user['username']):
                sys.stderr.write(
                    "Error: Username is invalid. "
                    "Use only letters, digits and underscores.\n")
                fail = True

            try:
                validate_email(user['email'])
            except exceptions.ValidationError:
                sys.stderr.write(
                    "Error: E-mail address '%s' is invalid.\n" % user['email'])
                fail = True

            if fail:
                sys.stderr.write(
                    "Skipping row for username '%s' due to errors\n"
                    % user['username'])
                fail_count += 1
                continue

            try:
                Person.objects.get(username=user['username'])
                sys.stderr.write(
                    "Error: Username '%s' exists. Skipping\n"
                    % user['username'])
                skip += 1
                continue
            except Person.DoesNotExist:
                pass

            try:
                institute = Institute.objects.get(name=user['institute'])
                user['institute'] = institute
            except Institute.DoesNotExist:
                sys.stderr.write(
                    "Error: Institute '%s' does not exist. Skipping\n"
                    % user['institute'])
                fail_count += 1
                continue

            project = None
            if user['project']:
                try:
                    project = Project.objects.get(pid=user['project'])
                except Project.DoesNotExist:
                    sys.stderr.write(
                        "Error: Project '%s' does not exist. Skipping\n"
                        % user['project'])
                    fail_count += 1
                    continue

            user['password1'] = user['password']
            person = Person.objects.create_user(**user)
            print("Successfully added user '%s'" % person)
            if project:
                add_user_to_project(person, project)

            success += 1

        print('')
        print('Added:   %s' % success)
        print('Skipped: %s' % skip)
        print('Failed:  %s' % fail_count)

        sys.exit(0)
