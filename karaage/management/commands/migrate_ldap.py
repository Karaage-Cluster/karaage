# Copyright 2014-2015 VPAC
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

from karaage.people.models import Person
from karaage.machines.models import Account, MachineCategory
from karaage.datastores import get_kg27_datastore
from karaage.datastores import get_global_test_datastore
from karaage.datastores import get_machine_category_test_datastore
import karaage.datastores.ldap as dldap


def _eq(dn1, dn2):
    dn1 = dn2str(str2dn(dn1)).lower()
    dn2 = dn2str(str2dn(dn2)).lower()
    return dn1 == dn2


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
        optparse.make_option(
            '--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete records that are no longer used.'),
    )

    def get_base(self, datastore, key):
        if key in datastore._settings:
            base_dn = datastore._settings[key]
        else:
            connection = tldap.connections[datastore._using]
            base_dn = connection.settings_dict[key]
        return base_dn

    def create_base(self, datastore, create_dn):
        base_dn = dn2str(str2dn(create_dn)[1:])

        try:
            organizationalUnit.objects.using(
                using=datastore._using, settings=datastore._settings) \
                .base_dn(base_dn) \
                .get(dn=create_dn)
        except organizationalUnit.DoesNotExist:
            print("Creating %s" % create_dn)
            organizationalUnit.objects.using(
                using=datastore._using, settings=datastore._settings) \
                .base_dn(base_dn) \
                .create(dn=create_dn)

    @django.db.transaction.atomic
    @tldap.transaction.commit_on_success
    def handle(self, **options):
        delete = options['delete']
        dry_run = options['dry_run']

        self.handle_global(delete, dry_run)

        # recurse through every datastore
        for mc in MachineCategory.objects.all():
            print("")
            print("Processing %s" % mc)
            print("==========================================================")
            self.handle_machine_category(mc, delete, dry_run)

    def handle_global(self, delete, dry_run):
        try:
            global_datastore = get_global_test_datastore(0)
            assert isinstance(global_datastore, dldap.GlobalDataStore)
        except IndexError:
            global_datastore = None

        if global_datastore is not None:
            # we need to keep the people
            person_base_dn = self.get_base(
                global_datastore, 'LDAP_PERSON_BASE')
            pgroup_base_dn = self.get_base(
                global_datastore, 'LDAP_GROUP_BASE')
        else:
            # we need to destroy the people and keep the accounts
            person_base_dn = None
            pgroup_base_dn = None

        # create the base dn
        # note we do this even if --dry-run given, as otherwise
        # we get confused if dn doesn't exist
        if global_datastore is not None:
            self.create_base(global_datastore, person_base_dn)
            self.create_base(global_datastore, pgroup_base_dn)

    def handle_machine_category(self, mc, delete, dry_run):
        # if datastore name is not ldap, we are not interested
        if mc.datastore != "ldap":
            print(
                "machine category %s datastore %s is not LDAP; nothing to do"
                % (mc, mc.datastore))
            return

        # retreive the LDAP datastores
        kg27_datastore = get_kg27_datastore()
        if kg27_datastore is None:
            print("KG27_DATASTORE not set; nothing to do")
            return
        try:
            global_datastore = get_global_test_datastore(0)
            assert isinstance(global_datastore, dldap.GlobalDataStore)
        except IndexError:
            global_datastore = None
        machine_category_datastore = get_machine_category_test_datastore(
            mc.datastore, 0)
        assert isinstance(
            machine_category_datastore, dldap.MachineCategoryDataStore)

        # get the base dn
        kg27_account_dn = self.get_base(kg27_datastore, 'LDAP_ACCOUNT_BASE')
        kg27_group_dn = self.get_base(kg27_datastore, 'LDAP_GROUP_BASE')

        if global_datastore is not None:
            # we need to keep the people
            person_base_dn = self.get_base(
                global_datastore, 'LDAP_PERSON_BASE')
            pgroup_base_dn = self.get_base(
                global_datastore, 'LDAP_GROUP_BASE')
        else:
            # we need to destroy the people and keep the accounts
            person_base_dn = None
            pgroup_base_dn = None

        account_base_dn = self.get_base(
            machine_category_datastore, 'LDAP_ACCOUNT_BASE')
        agroup_base_dn = self.get_base(
            machine_category_datastore, 'LDAP_GROUP_BASE')

        # create the base dn
        # note we do this even if --dry-run given, as otherwise
        # we get confused if dn doesn't exist
        self.create_base(machine_category_datastore, account_base_dn)
        self.create_base(machine_category_datastore, agroup_base_dn)

        # sanity check
        assert pgroup_base_dn != agroup_base_dn
        assert person_base_dn != account_base_dn

        # process kg27 people/accounts
        for p in kg27_datastore._accounts() \
                .base_dn(kg27_account_dn):

            delete_this = delete

            # if this is an account, copy to new place
            if 'posixAccount' in p.objectClass:
                # this was an account; then there was no person in LDAP

                # copy account to correct place
                try:
                    dst = machine_category_datastore._accounts().get(uid=p.uid)
                    if _eq(p.dn, dst.dn):
                        delete_this = False
                    if 'posixAccount' not in dst.objectClass:
                        delete_this = False

                        # This shouldn't normally ever happen.
                        if dry_run:
                            print(
                                "Conflicting person exists, would delete "
                                "person %s " % dst.dn)
                        else:
                            print(
                                "Conflicting person exists, deleting "
                                "person %s " % dst.dn)
                            dst.delete()
                        raise machine_category_datastore._person.DoesNotExist
                except machine_category_datastore._account.DoesNotExist:
                    new_account = machine_category_datastore._create_account()
                    for i, _ in new_account.get_fields():
                        if i != "objectClass":
                            value = getattr(p, i)
                            setattr(new_account, i, value)

                    if dry_run:
                        print(
                            "Would copy account %s to account %s"
                            % (p.dn, account_base_dn))
                    else:
                        new_account.save()
                        print(
                            "Copying account %s to account %s"
                            % (p.dn, new_account.dn))

            # all kg27 entries are persons, copy person to correct place
            if global_datastore is not None:
                if 'posixAccount' in p.objectClass:
                    # we are looking at an account, we need to get the person
                    account = Account.objects.get(
                        username=p.uid, machine_category=mc)
                    person = Person.objects.get(account=account)
                    uid = person.username
                else:
                    # we are looking at a person, we already have the uid
                    uid = p.uid

                # Create person, if required.  This is better then calling
                # person.save() as we get the password too.
                try:
                    dst = global_datastore._people().get(uid=uid)
                    if _eq(p.dn, dst.dn):
                        delete_this = False
                    if 'posixAccount' in dst.objectClass:
                        delete_this = False
                        if dry_run:
                            print(
                                "Conflicting account exists, would delete "
                                "account %s " % dst.dn)
                        else:
                            print(
                                "Conflicting account exists, deleting "
                                "account %s " % dst.dn)
                            dst.delete()
                        raise global_datastore._person.DoesNotExist

                except global_datastore._person.DoesNotExist:
                    new_person = global_datastore._create_person()
                    for i, _ in new_person.get_fields():
                        if i != "objectClass":
                            value = getattr(p, i)
                            setattr(new_person, i, value)

                    if dry_run:
                        print(
                            "Would copy account %s to person %s"
                            % (p.dn, person_base_dn))
                    else:
                        new_person.save()
                        print(
                            "Copying account %s to person %s"
                            % (p.dn, new_person.dn))

            if delete_this:
                if dry_run:
                    print("Would delete %s" % p.dn)
                else:
                    print("deleting %s" % p.dn)
                    p.delete()

        # process groups
        for g in kg27_datastore._groups() \
                .base_dn(kg27_group_dn):

            delete_this = delete

            if global_datastore is not None:
                try:
                    dst = global_datastore._groups().get(cn=g.cn)
                    if _eq(g.dn, dst.dn):
                        delete_this = False
                except global_datastore._group.DoesNotExist:
                    new_group = global_datastore._create_group()
                    for i, _ in new_group.get_fields():
                        if i != "objectClass":
                            value = getattr(g, i)
                            setattr(new_group, i, value)

                    if dry_run:
                        print("Would copy group %s to %s"
                              % (g.dn, pgroup_base_dn))
                    else:
                        new_group.save()
                        print("Copying group %s to %s" % (g.dn, new_group.dn))

            try:
                dst = machine_category_datastore._groups().get(cn=g.cn)
                if _eq(g.dn, dst.dn):
                    delete_this = False
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

            if delete_this:
                if dry_run:
                    print("Would delete %s" % g.dn)
                else:
                    print("deleting %s" % g.dn)
                    g.delete()
