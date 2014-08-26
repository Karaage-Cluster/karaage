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
from tldap.dn import dn2str, str2dn
from tldap.schemas.rfc import organizationalUnit

from karaage.people.models import Group
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

    def create_base(self, datastore, key):
        if key in datastore._settings:
            create_dn = datastore._settings[key]
        else:
            connection = tldap.connections[datastore._using]
            create_dn = connection.settings_dict[key]

        base_dn = dn2str(str2dn(create_dn)[1:])

        _, c = organizationalUnit.objects.using(
            using=datastore._using, settings=datastore._settings) \
            .base_dn(base_dn) \
            .get_or_create(dn=create_dn)

        if c:
            print("Created %s" % create_dn)
        else:
            print("Base already exists %s" % create_dn)

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

        self.create_base(global_datastore, 'LDAP_PERSON_BASE')
        self.create_base(global_datastore, 'LDAP_GROUP_BASE')
        self.create_base(machine_category_datastore, 'LDAP_ACCOUNT_BASE')
        self.create_base(machine_category_datastore, 'LDAP_GROUP_BASE')

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

            # Ensure all groups exist, as required.
            for group in Group.objects.iterator():
                print("updating group %s members (people)" % group)
                group.save()

                for person in group.members.filter(is_active=True):
                    global_datastore.add_person_to_group(person, group)

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

# not needed.
#        for group in Group.objects.iterator():
#            print("updating group %s members (accounts)" % group)
#            accounts = Account.objects \
#                .filter(person__groups=group, machine_category__pk=1,
#                    date_deleted__isnull=True)
#            for account in accounts.iterator():
#                print account
#                machine_category_datastore.add_account_to_group(
#                    account, group)
