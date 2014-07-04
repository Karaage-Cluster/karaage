# Copyright 2007-2014 VPAC
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

import optparse

from django.core.management.base import BaseCommand
import django.db.transaction
import tldap.transaction
import tldap.dn

from karaage.machines.models import Account
from karaage.datastores import get_global_test_datastore
from karaage.datastores import get_machine_category_test_datastore
import karaage.datastores.ldap as dldap


class Command(BaseCommand):
    help = "Run migrations on the LDAP database."

    option_list = BaseCommand.option_list + (
        optparse.make_option(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Don\'t change anything, output what needs '
            'to change instead.'),
        )

    @django.db.transaction.commit_on_success
    @tldap.transaction.commit_on_success
    def handle(self, **options):
        try:
            global_datastore = get_global_test_datastore(0)
            assert isinstance(global_datastore, dldap.GlobalDataStore)
        except IndexError:
            global_datastore = None
        machine_category_datastore = get_machine_category_test_datastore(
            "ldap", 0)
        assert isinstance(
            machine_category_datastore, dldap.MachineCategoryDataStore)

        if global_datastore is not None:
            # we have to move accounts to the account_base.
            # no changes rquired for people.
            account_base_dn = machine_category_datastore._accounts(
                ).get_base_dn()

            for p in global_datastore._people().filter(
                    objectClass='posixAccount'):
                # Convert account to person, strip unwanted fields.
                # This is better then calling person.save() as we get the
                # password too.
                new_person = global_datastore._create_person(dn=p.dn)
                for i, _ in new_person.get_fields():
                    if i != "objectClass":
                        value = getattr(p, i)
                        setattr(new_person, i, value)

                if options['dry_run']:
                    print(
                        "would move account from "
                        "%s to %s" % (p.dn, account_base_dn))
                    print("would create person for %s" % p.dn)
                else:
                    # move account from person to accounts
                    print(
                        "moving account from "
                        "%s to %s" % (p.dn, account_base_dn))
                    p.rename(new_base_dn=account_base_dn)

                    # write person entry, if not already existing
                    print("creating person for %s" % p.dn)
                    try:
                        new_person.save()
                    except machine_category_datastore._account.AlreadyExists:
                        pass

        else:
            # people not in LDAP, delete people without accounts.

            for p in machine_category_datastore._accounts():
                # If there are no accounts for this person, then delete
                # the LDAP entry.
                ua = Account.objects.filter(
                    username=p.uid, date_deleted__isnull=True)
                if ua.count() == 0 and 'posixAccount' not in p.objectClass:
                    if options['dry-run']:
                        print("would delete %s" % p.dn)
                    else:
                        print("deleting %s" % p.dn)
                        p.delete()
