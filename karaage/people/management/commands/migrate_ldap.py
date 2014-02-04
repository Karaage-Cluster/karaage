# Copyright 2007-2013 VPAC
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
import ldif
import optparse

from django.core.management.base import BaseCommand
import django.db.transaction
import tldap.transaction

from karaage.machines.models import Account
from karaage.datastores import get_test_datastore

class Command(BaseCommand):
    help = "Run migrations on the LDAP database."

    option_list = BaseCommand.option_list + (
        optparse.make_option('--ldif',
        action='store_true',
        dest='ldif',
        default=False,
        help='Don\'t change anything, output ldif of what needs to change instead.'),
    )

    @django.db.transaction.commit_on_success
    @tldap.transaction.commit_on_success
    def handle(self, **options):
        datastore = get_test_datastore("ldap", 0)
        if options['ldif']:
            ldif_writer=ldif.LDIFWriter(sys.stdout)

        for p in datastore._accounts():
            # If there are no accounts for this person, then delete
            # the LDAP entry.
            ua = Account.objects.filter(username=p.uid, date_deleted__isnull=True)
            if ua.count() == 0 and 'posixAccount' not in p.objectClass:
                if options['ldif']:
                    entry = { 'changetype': [ 'delete' ] }
                    ldif_writer.unparse(p.dn,entry)
                else:
                    p.delete()
