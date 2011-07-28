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

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

import sys

class Command(BaseCommand):
    help = 'Change a users username'
    args = '<old username> <new username>'

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError('Usage: change_username <old username> <new username>')
        old = args[0]
        new = args[1]

        try:
            user = User.objects.get(username=old)
        except User.DoesNotExist:
            raise CommandError('user %s does not exist' % old)
        
        try:
            user = User.objects.get(username=new)
            raise CommandError('new username %s already exists' % new)
        except User.DoesNotExist:
            pass

        while 1:
            confirm = raw_input('Change user "%s" to "%s (yes,no): ' % (old, new))
            if confirm == 'yes':
                break
            elif confirm == 'no':
                return sys.exit(0)
            else:
                print "Please enter yes or no"
        
    
        user = User.objects.get(username=old)
        person = user.get_profile()

        from karaage.datastores import change_username
        change_username(person, new)
        print "Changed datastore username (LDAP/AD etc.)"

        for account in person.useraccount_set.all():
            if account.username == old:
                account.username = new
                account.save()
                print "Changed username on %s account" % account.machine_category
        
        user.username = new
        user.save()
        print "Changed Karaage username"
        print "Done"

