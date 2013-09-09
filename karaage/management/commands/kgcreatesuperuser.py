# Copyright 2007-2010 VPAC
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
Management utility to create superusers.
"""

import getpass
import os
import re
import sys
from optparse import make_option
from django.core import exceptions
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from karaage.people.models import Person
from karaage.institutes.models import Institute
from karaage.people.utils import validate_username, UsernameException

import django.db.transaction
import tldap.transaction

EMAIL_RE = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'  # quoted-string
    r')@(?:[A-Z0-9-]+\.)+[A-Z]{2,6}$', re.IGNORECASE)  # domain


def is_valid_email(value):
    if not EMAIL_RE.search(value):
        raise exceptions.ValidationError(_('Enter a valid e-mail address.'))


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--username', '-u', help='Username'),
        make_option('--email', '-e', help='E-Mail'),
        make_option('--short_name', '-f', help='Short Name'),
        make_option('--full_name', '-l', help='Full Name'),
        make_option('--password', '-p', help='Password'),
        make_option('--institute', '-i', help='Institute Name'),
    )
    help = 'Used to create a karaage superuser.'

    @django.db.transaction.commit_on_success
    @tldap.transaction.commit_on_success
    def handle(self, *args, **options):
 
        username = options['username']
        email = options['email']
        short_name = options['short_name']
        long_name = options['long_name']
        password = options['password']
        institute_name = options['institute']

        # Try to determine the current system user's username to use as a default.
        try:
            import pwd
            default_username = pwd.getpwuid(os.getuid())[0].replace(' ', '').lower()
            if default_username == 'root':
                default_username = ''
        except (ImportError, KeyError):
            # KeyError will be raised by getpwuid() if there is no
            # corresponding entry in the /etc/passwd file (a very restricted
            # chroot environment, for example).
            default_username = ''

        # Determine whether the default username is taken, so we don't display
        # it as an option.
        if default_username:
            try:
                Person.objects.get(username=default_username)
            except Person.DoesNotExist:
                pass
            else:
                default_username = ''

        # Prompt for username/email/password. Enclose this whole thing in a
        # try/except to trap for a keyboard interrupt and exit gracefully.
        try:
            # Get a username
            while 1:
                if not username:
                    input_msg = 'Username'
                    if default_username:
                        input_msg += ' (Leave blank to use %r)' % default_username
                    username = raw_input(input_msg + ': ')
                    if default_username and username=='':
                        username = default_username
                try:
                    validate_username(username)
                    break
                except UsernameException, e:
                    sys.stderr.write("%s\n" % e)
                    username = None
                    continue
                
            # Get an email
            while 1:
                if not email:
                    email = raw_input('E-mail address: ')
                try:
                    is_valid_email(email)
                except exceptions.ValidationError:
                    sys.stderr.write("Error: That e-mail address is invalid.\n")
                    email = None
                else:
                    break
            
            # Get a password
            while 1:
                if not password:
                    password = getpass.getpass()
                    password2 = getpass.getpass('Password (again): ')
                    if password != password2:
                        sys.stderr.write("Error: Your passwords didn't match.\n")
                        password = None
                        continue
                if password.strip() == '':
                    sys.stderr.write("Error: Blank passwords aren't allowed.\n")
                    password = None
                    continue
                break

            while 1:
                if not short_name:
                    short_name = raw_input('Short Name: ')
                else:
                    break
            while 1:
                if not full_name:
                    full_name = raw_input('Full Name: ')
                else:
                    break

            if Institute.objects.count() == 0:
                if not institute_name:
                    print "No Institutes in system will create one now"
                while 1:
                    if not institute_name:
                        institute_name = raw_input('New Institute Name: ')
                    else:
                        break
                institute = Institute.objects.create(name=institute_name, is_active=True)
            else:
                if not institute_name:
                    print "Choose an existing institute for new superuser:"
                    print "Valid choices are:"
                    for i in Institute.active.all():
                        print i
                while 1:
                    if not institute_name:
                        institute_name = raw_input('Institute Name: ')
                    try:
                        institute = Institute.objects.get(name=institute_name)
                    except Institute.DoesNotExist:
                        sys.stderr.write("Error: Institute does not exist\n")
                        institute_name = None
                        continue
                    break
                    
        except KeyboardInterrupt:
            sys.stderr.write("\nOperation cancelled.\n")
            sys.exit(1)

        data = {
            'username': username,
            'email': email,
            'password': password,
            'short_name': short_name,
            'full_name': full_name,
            'institute': institute,
            }
        person = Person.objects.create_superuser(**data)
        print "Karaage Superuser created successfully."
