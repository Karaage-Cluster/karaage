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
import ldap.dn
import optparse

from django.core.management.base import BaseCommand
import django.db.transaction
import tldap.transaction

from karaage.machines.models import Account
from karaage.datastores import get_test_datastore
import karaage.datastores.ldap as dldap

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
        assert isinstance(datastore, dldap.AccountDataStore)

        if options['ldif']:
            ldif_writer=ldif.LDIFWriter(sys.stdout)

        if datastore._person is not None:
            # we have to move accounts to the account_base.
            # no changes rquired for people.
            account_base_dn = datastore._accounts().get_base_dn()
            split_account_base_dn = ldap.dn.str2dn(account_base_dn)

            for p in datastore._people().filter(objectClass='posixAccount'):
                # Convert account to person, strip unwanted fields.
                # This is better then calling person.save() as we get the
                # password too.
                new_person = datastore._create_person(dn=p.dn)
                for i, _ in new_person.get_fields():
                    if i != "objectClass":
                        value = getattr(p, i)
                        setattr(new_person, i, value)

                if options['ldif']:
                    # calculate fully qualified new DN.
                    split_dn = ldap.dn.str2dn(p.dn)
                    tmp = []
                    tmp.append(split_dn[0])
                    tmp.extend(split_account_base_dn)
                    new_dn = ldap.dn.dn2str(tmp)

                    # we can do move in ldif, so delete and add
                    entry = { 'changetype': [ 'delete' ] }
                    ldif_writer.unparse(p.dn,entry)

                    # write person entry
                    if new_person.pwdAttribute is None:
                        new_person.pwdAttribute = 'userPassword'
                    new_person.unparse(ldif_writer,
                            None, { 'changetype': [ 'add' ] } )

                    # write account entry
                    if p.pwdAttribute is None:
                        p.pwdAttribute = 'userPassword'
                    p.unparse(ldif_writer, new_dn, { 'changetype': [ 'add' ] } )
                else:
                    # move account from person to accounts
                    print "moving account and creating person for %s" % p.dn
                    p.rename(new_base_dn=account_base_dn)
                    # write person entry, if not already existing
                    try:
                        new_person.save()
                    except account_person._account.AlreadyExists:
                        pass

        else:
            # people not in LDAP, delete people without accounts.

            for p in datastore._accounts():
                # If there are no accounts for this person, then delete
                # the LDAP entry.
                ua = Account.objects.filter(username=p.uid, date_deleted__isnull=True)
                if ua.count() == 0 and 'posixAccount' not in p.objectClass:
                    if options['ldif']:
                        entry = { 'changetype': [ 'delete' ] }
                        ldif_writer.unparse(p.dn,entry)
                    else:
                        print "deleting %s" % p.dn
                        p.delete()
