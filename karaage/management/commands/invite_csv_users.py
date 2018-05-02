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
# along with Karaage  If not, see <http://www.gnu.org/licenses/>.i

"""
Management utility to initiate a bulk invitation mailout from a
CSV file.

CSV format should be:
username,password,short_name,full_name,email,institute,project
sam,secret,Joe,Joe Bloggs,joe@example.com,Test,TestProject2

"""

import csv
import re
import sys

import django.db.transaction
import tldap.transaction
from django.core import exceptions
from django.core.management.base import BaseCommand
from django.core.validators import validate_email

from karaage.institutes.models import Institute
from karaage.plugins.kgapplications import emails
from karaage.plugins.kgapplications.models import ProjectApplication
from karaage.plugins.kgapplications.views import base
from karaage.plugins.kgapplications.views.project import (
    get_applicant_from_email,
)
from karaage.projects.models import Project


RE_VALID_USERNAME = re.compile('[\w.@+-]+$')


class Command(BaseCommand):
    help = """Initiate bulk invitation a CSV file with the following format:
username,password,short_name,full_name,email,institute,project"""
    args = "csvfile"

    @django.db.transaction.non_atomic_requests
    @tldap.transaction.commit_on_success
    def handle(self, csvfile, **options):
        verbosity = int(options.get('verbosity', 1))

        try:
            data = csv.DictReader(open(csvfile))
        except csv.Error as e:
            sys.stderr.write("ERROR: Failed to read CSV file.\n")
            sys.exit(1)

        success = 0
        fail_count = 0
        skip = 0
        for user in data:
            fail = False

            if verbosity >= 1:
                print("Attempting to send an invite to user '%s' at '%s'" % (user['username'], user['email']))

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

            applicant, existing_person = get_applicant_from_email(user['email'])
            if existing_person:
                print("skipping %s:%s, user already exists" % (user['username'], user['email']))
                skip += 1
                continue

            application = ProjectApplication()
            applicant.short_name = user["short_name"]
            applicant.full_name = user["full_name"]
            applicant.username = user["username"]
            application.applicant = applicant
            application.project = project
            application.state = ProjectApplication.OPEN
            application.header_message = "Please select your institute and hit the 'SAML login' button when prompted"
            application.reopen()

            email_link, is_secret = base.get_email_link(application)
            emails.send_invite_email(application, email_link, is_secret)
            success += 1

        print('')
        print('Added:   %s' % success)
        print('Skipped: %s' % skip)
        print('Failed:  %s' % fail_count)

        sys.exit(0)
