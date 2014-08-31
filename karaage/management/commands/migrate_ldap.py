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

    def get_base(self, datastore, key):
        if key in datastore._settings:
            base_dn = datastore._settings[key]
        else:
            connection = tldap.connections[datastore._using]
            base_dn = connection.settings_dict[key]
        return base_dn

    def create_base(self, datastore, key, dry_run):
        create_dn = self.get_base(datastore, key)
        base_dn = dn2str(str2dn(create_dn)[1:])

        try:
            organizationalUnit.objects.using(
                using=datastore._using, settings=datastore._settings) \
                .base_dn(base_dn) \
                .get(dn=create_dn)
        except organizationalUnit.DoesNotExist:
            if dry_run:
                print("Would create %s" % create_dn)
            else:
                print("Creating %s" % create_dn)
                organizationalUnit.objects.using(
                    using=datastore._using, settings=datastore._settings) \
                    .base_dn(base_dn) \
                    .create(dn=create_dn)

    @django.db.transaction.commit_on_success
    @tldap.transaction.commit_on_success
    def handle(self, **options):
        dry_run = options['dry_run']

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
            self.create_base(
                global_datastore, 'LDAP_PERSON_BASE', dry_run)
            self.create_base(
                global_datastore, 'LDAP_GROUP_BASE', dry_run)

        self.create_base(
            machine_category_datastore, 'LDAP_ACCOUNT_BASE', dry_run)
        self.create_base(
            machine_category_datastore, 'LDAP_GROUP_BASE', dry_run)

        # we have to move accounts to the account_base.
        # no changes required for people.
        try:
            old_account_dn = self.get_base(
                machine_category_datastore, 'OLD_ACCOUNT_BASE')
            old_group_dn = self.get_base(
                machine_category_datastore, 'OLD_GROUP_BASE')
        except KeyError:
            print("OLD_* settings not defined, nothing to do, exiting.")
            return

        old_account_dn = dn2str(str2dn(old_account_dn))
        old_group_dn = dn2str(str2dn(old_group_dn))

        if global_datastore is not None:
            # we need to keep the people
            person_base_dn = self.get_base(
                global_datastore, 'LDAP_PERSON_BASE')
            person_base_dn = dn2str(str2dn(person_base_dn))
            pgroup_base_dn = self.get_base(
                global_datastore, 'LDAP_GROUP_BASE')
            pgroup_base_dn = dn2str(str2dn(pgroup_base_dn))
        else:
            # we need to destroy the people and keep the accounts
            person_base_dn = None
            pgroup_base_dn = None

        account_base_dn = self.get_base(
            machine_category_datastore, 'LDAP_ACCOUNT_BASE')
        account_base_dn = dn2str(str2dn(account_base_dn))

        agroup_base_dn = self.get_base(
            machine_category_datastore, 'LDAP_GROUP_BASE')
        agroup_base_dn = dn2str(str2dn(agroup_base_dn))

        assert pgroup_base_dn != agroup_base_dn
        assert person_base_dn != account_base_dn

        # process accounts
        for p in machine_category_datastore._accounts() \
                .base_dn(old_account_dn) \
                .filter(objectClass='posixAccount'):

            if 'posixAccount' in p.objectClass:
                # this was an account; then there was no person in LDAP

                # move account to correct place
                if old_account_dn != account_base_dn:
                    if dry_run:
                        print(
                            "Would move account from "
                            "%s to %s" % (p.dn, account_base_dn))
                    else:
                        # move account from person to accounts
                        print(
                            "Moving account from "
                            "%s to %s" % (p.dn, account_base_dn))
                        p.rename(new_base_dn=account_base_dn)

                if global_datastore is not None:
                    # Create person, if required.  This is better then calling
                    # person.save() as we get the password too.
                    try:
                        dst = global_datastore._people().get(uid=p.uid)
                        if 'posixAccount' in dst.objectClass:
                            if dry_run:
                                print(
                                    "Would copy person %s to %s"
                                    % (p.dn, person_base_dn))
                            else:
                                print(
                                    "Unexpected account exists, not copying "
                                    "person %s to %s" % (p.dn, person_base_dn))

                    except global_datastore._person.DoesNotExist:
                        new_person = global_datastore._create_person()
                        for i, _ in new_person.get_fields():
                            if i != "objectClass":
                                value = getattr(p, i)
                                setattr(new_person, i, value)

                        if dry_run:
                            print(
                                "Would copy person %s to %s"
                                % (p.dn, person_base_dn))
                        else:
                            new_person.save()
                            print(
                                "Copying person %s to %s"
                                % (p.dn, new_person.dn))
            else:
                # this wasn't an account, it was a person

                if global_datastore is not None:
                    # move person if required
                    if old_account_dn != person_base_dn:
                        if dry_run:
                            print(
                                "Would move person from "
                                "%s to %s" % (p.dn, person_base_dn))
                        else:
                            # move account from person to accounts
                            print(
                                "Moving person from "
                                "%s to %s" % (p.dn, person_base_dn))
                            p.rename(new_base_dn=person_base_dn)
                else:
                    # person not required, delete
                    if options['dry-run']:
                        print("Would delete %s" % p.dn)
                    else:
                        print("Deleting %s" % p.dn)
                        p.delete()

        # process groups
        for g in machine_category_datastore._groups() \
                .base_dn(old_group_dn):

            delete = True

            if global_datastore is not None:
                try:
                    global_datastore._groups().get(cn=g.cn)
                    delete = False
                except global_datastore._group.DoesNotExist:
                    new_group = global_datastore._create_group()
                    for i, _ in new_group.get_fields():
                        if i != "objectClass":
                            value = getattr(g, i)
                            setattr(new_group, i, value)

                    if dry_run:
                        print("Would copy group %s to %s"
                              % (g.dn, agroup_base_dn))
                    else:
                        new_group.save()
                        print("Copying group %s to %s" % (g.dn, new_group.dn))

            try:
                machine_category_datastore._groups().get(cn=g.cn)
                delete = False
            except machine_category_datastore._group.DoesNotExist:
                new_group = machine_category_datastore._create_group()
                for i, _ in new_group.get_fields():
                    if i != "objectClass":
                        value = getattr(g, i)
                        setattr(new_group, i, value)

                if dry_run:
                    print("Would copy group %s to %s" % (g.dn, agroup_base_dn))
                else:
                    new_group.save()
                    print("Copying group %s to %s" % (g.dn, new_group.dn))

            if delete:
                # group not required, delete
                if options['dry-run']:
                    print("Would delete %s" % g.dn)
                else:
                    print("Deleting %s" % g.dn)
                    g.delete()
