# Copyright 2013-2015 VPAC
# Copyright 2014 The University of Melbourne
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

import six

import tldap.schemas as schemas
import tldap.schemas.ad
import tldap.schemas.rfc
import tldap.schemas.ds389
import tldap.methods as methods
import tldap.methods.ad
import tldap.methods.common
import tldap.methods.pwdpolicy
import tldap.methods.ds389
import tldap.manager


def _a(string):
    """ Force string to ASCII only characters. """
    string = ''.join(c for c in string if 31 < ord(c) < 127)
    return string


class PersonMixin(object):

    @classmethod
    def pre_save(cls, self):
        full_name = getattr(self, "fullName", None)
        if full_name is None:
            full_name = "%s %s" % (self.givenName, self.sn)

        self.displayName = six.u('%s (%s)') % (full_name, self.o)


class AccountMixin(object):

    @classmethod
    def pre_save(cls, self):
        full_name = getattr(self, "fullName", None)
        if full_name is None:
            full_name = "%s %s" % (self.givenName, self.sn)

        self.displayName = six.u('%s (%s)') % (full_name, self.o)
        self.gecos = _a(six.u('%s (%s)') % (full_name, self.o))


############
# OpenLDAP #
############

class openldap_person(methods.baseMixin):

    schema_list = [
        schemas.rfc.person,
        schemas.rfc.organizationalPerson,
        schemas.rfc.inetOrgPerson,
        schemas.rfc.pwdPolicy,
    ]

    mixin_list = [
        methods.common.personMixin,
        methods.pwdpolicy.pwdPolicyMixin,
        PersonMixin,
    ]

    class Meta:
        base_dn_setting = "LDAP_PERSON_BASE"
        object_classes = {'top'}
        search_classes = {'person'}
        pk = 'uid'

    managed_by = tldap.manager.ManyToOneDescriptor(
        this_key='manager',
        linked_cls='karaage.datastores.ldap_schemas.openldap_person',
        linked_key='dn')
    manager_of = tldap.manager.OneToManyDescriptor(
        this_key='dn',
        linked_cls='karaage.datastores.ldap_schemas.openldap_person',
        linked_key='manager')


class openldap_account(methods.baseMixin):

    schema_list = [
        schemas.rfc.person,
        schemas.rfc.organizationalPerson,
        schemas.rfc.inetOrgPerson,
        schemas.rfc.posixAccount,
        schemas.rfc.shadowAccount,
        schemas.rfc.pwdPolicy,
    ]

    mixin_list = [
        methods.common.personMixin,
        methods.common.accountMixin,
        methods.pwdpolicy.pwdPolicyMixin,
        AccountMixin,
    ]

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = {'top'}
        search_classes = {'posixAccount'}
        pk = 'uid'

    managed_by = tldap.manager.ManyToOneDescriptor(
        this_key='manager',
        linked_cls='karaage.datastores.ldap_schemas.openldap_account',
        linked_key='dn')
    manager_of = tldap.manager.OneToManyDescriptor(
        this_key='dn',
        linked_cls='karaage.datastores.ldap_schemas.openldap_account',
        linked_key='manager')
    unixHomeDirectory = tldap.manager.AliasDescriptor("homeDirectory")


class openldap_kg27(methods.baseMixin):

    schema_list = [
        schemas.rfc.person,
        schemas.rfc.organizationalPerson,
        schemas.rfc.inetOrgPerson,
        schemas.rfc.posixAccount,
        schemas.rfc.shadowAccount,
        schemas.rfc.pwdPolicy,
    ]

    mixin_list = [
        methods.common.personMixin,
        methods.common.accountMixin,
        methods.pwdpolicy.pwdPolicyMixin,
        AccountMixin,
    ]

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = {'top'}
        # this will find people and accounts
        search_classes = {'person'}
        pk = 'uid'

    managed_by = tldap.manager.ManyToOneDescriptor(
        this_key='manager',
        linked_cls='karaage.datastores.ldap_schemas.openldap_kg27',
        linked_key='dn')
    manager_of = tldap.manager.OneToManyDescriptor(
        this_key='dn',
        linked_cls='karaage.datastores.ldap_schemas.openldap_kg27',
        linked_key='manager')
    unixHomeDirectory = tldap.manager.AliasDescriptor("homeDirectory")


class openldap_person_group(methods.baseMixin):

    schema_list = [schemas.rfc.posixGroup]
    mixin_list = [methods.common.groupMixin]

    class Meta:
        base_dn_setting = "LDAP_GROUP_BASE"
        object_classes = {'top'}
        search_classes = {'posixGroup'}
        pk = 'cn'

    # people
    secondary_people = tldap.manager.ManyToManyDescriptor(
        this_key='memberUid',
        linked_cls=openldap_person, linked_key='uid', linked_is_p=False,
        related_name="secondary_groups")


class openldap_account_group(methods.baseMixin):

    schema_list = [schemas.rfc.posixGroup]
    mixin_list = [methods.common.groupMixin]

    class Meta:
        base_dn_setting = "LDAP_GROUP_BASE"
        object_classes = {'top'}
        search_classes = {'posixGroup'}
        pk = 'cn'

    # accounts
    primary_accounts = tldap.manager.OneToManyDescriptor(
        this_key='gidNumber',
        linked_cls=openldap_account, linked_key='gidNumber',
        related_name="primary_group")
    secondary_accounts = tldap.manager.ManyToManyDescriptor(
        this_key='memberUid',
        linked_cls=openldap_account, linked_key='uid', linked_is_p=False,
        related_name="secondary_groups")


class openldap_kg27_group(methods.baseMixin):

    schema_list = [schemas.rfc.posixGroup]
    mixin_list = [methods.common.groupMixin]

    class Meta:
        base_dn_setting = "LDAP_GROUP_BASE"
        object_classes = {'top'}
        search_classes = {'posixGroup'}
        pk = 'cn'

    # accounts
    primary_accounts = tldap.manager.OneToManyDescriptor(
        this_key='gidNumber',
        linked_cls=openldap_kg27, linked_key='gidNumber',
        related_name="primary_group")
    secondary_accounts = tldap.manager.ManyToManyDescriptor(
        this_key='memberUid',
        linked_cls=openldap_kg27, linked_key='uid', linked_is_p=False,
        related_name="secondary_groups")


############
# 389 LDAP #
############

class ds389AccountMixin(object):

    @classmethod
    def pre_save(cls, self):
        # work around for https://bugzilla.redhat.com/show_bug.cgi?id=1171308
        if self.userPassword is None:
            from karaage.people.models import Person
            self.change_password(Person.objects.make_random_password())


class ds389_person(methods.baseMixin):

    schema_list = [
        schemas.rfc.person,
        schemas.rfc.organizationalPerson,
        schemas.rfc.inetOrgPerson,
        schemas.ds389.passwordObject,
    ]

    mixin_list = [
        methods.common.personMixin,
        methods.ds389.passwordObjectMixin,
        PersonMixin,
        ds389AccountMixin,
    ]

    class Meta:
        base_dn_setting = "LDAP_PERSON_BASE"
        object_classes = {'top'}
        search_classes = {'person'}
        pk = 'uid'

    managed_by = tldap.manager.ManyToOneDescriptor(
        this_key='manager',
        linked_cls='karaage.datastores.ldap_schemas.ds389_person',
        linked_key='dn')
    manager_of = tldap.manager.OneToManyDescriptor(
        this_key='dn',
        linked_cls='karaage.datastores.ldap_schemas.ds389_person',
        linked_key='manager')


class ds389_account(methods.baseMixin):

    schema_list = [
        schemas.rfc.person,
        schemas.rfc.organizationalPerson,
        schemas.rfc.inetOrgPerson,
        schemas.rfc.posixAccount,
        schemas.rfc.shadowAccount,
        schemas.ds389.passwordObject,
    ]

    mixin_list = [
        methods.common.personMixin,
        methods.common.accountMixin,
        methods.ds389.passwordObjectMixin,
        AccountMixin,
        ds389AccountMixin,
    ]

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = {'top'}
        search_classes = {'posixAccount'}
        pk = 'uid'

    managed_by = tldap.manager.ManyToOneDescriptor(
        this_key='manager',
        linked_cls='karaage.datastores.ldap_schemas.ds389_account',
        linked_key='dn')
    manager_of = tldap.manager.OneToManyDescriptor(
        this_key='dn',
        linked_cls='karaage.datastores.ldap_schemas.ds389_account',
        linked_key='manager')
    unixHomeDirectory = tldap.manager.AliasDescriptor("homeDirectory")


class ds389_kg27(methods.baseMixin):

    schema_list = [
        schemas.rfc.person,
        schemas.rfc.organizationalPerson,
        schemas.rfc.inetOrgPerson,
        schemas.rfc.posixAccount,
        schemas.rfc.shadowAccount,
        schemas.ds389.passwordObject,
    ]

    mixin_list = [
        methods.common.personMixin,
        methods.common.accountMixin,
        methods.ds389.passwordObjectMixin,
        AccountMixin,
    ]

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = {'top'}
        search_classes = {'person'}
        pk = 'uid'

    managed_by = tldap.manager.ManyToOneDescriptor(
        this_key='manager',
        linked_cls='karaage.datastores.ldap_schemas.ds389_kg27',
        linked_key='dn')
    manager_of = tldap.manager.OneToManyDescriptor(
        this_key='dn',
        linked_cls='karaage.datastores.ldap_schemas.ds389_kg27',
        linked_key='manager')
    unixHomeDirectory = tldap.manager.AliasDescriptor("homeDirectory")


class ds389_person_group(methods.baseMixin):

    schema_list = [schemas.rfc.posixGroup]
    mixin_list = [methods.common.groupMixin]

    class Meta:
        base_dn_setting = "LDAP_GROUP_BASE"
        object_classes = {'top'}
        search_classes = {'posixGroup'}
        pk = 'cn'

    # people
    secondary_people = tldap.manager.ManyToManyDescriptor(
        this_key='memberUid',
        linked_cls=ds389_person, linked_key='uid', linked_is_p=False,
        related_name="secondary_groups")


class ds389_account_group(methods.baseMixin):

    schema_list = [schemas.rfc.posixGroup]
    mixin_list = [methods.common.groupMixin]

    class Meta:
        base_dn_setting = "LDAP_GROUP_BASE"
        object_classes = {'top'}
        search_classes = {'posixGroup'}
        pk = 'cn'

    # accounts
    primary_accounts = tldap.manager.OneToManyDescriptor(
        this_key='gidNumber',
        linked_cls=ds389_account, linked_key='gidNumber',
        related_name="primary_group")
    secondary_accounts = tldap.manager.ManyToManyDescriptor(
        this_key='memberUid',
        linked_cls=ds389_account, linked_key='uid', linked_is_p=False,
        related_name="secondary_groups")


class ds389_kg27_group(methods.baseMixin):

    schema_list = [schemas.rfc.posixGroup]
    mixin_list = [methods.common.groupMixin]

    class Meta:
        base_dn_setting = "LDAP_GROUP_BASE"
        object_classes = {'top'}
        search_classes = {'posixGroup'}
        pk = 'cn'

    # accounts
    primary_accounts = tldap.manager.OneToManyDescriptor(
        this_key='gidNumber',
        linked_cls=ds389_kg27, linked_key='gidNumber',
        related_name="primary_group")
    secondary_accounts = tldap.manager.ManyToManyDescriptor(
        this_key='memberUid',
        linked_cls=ds389_kg27, linked_key='uid', linked_is_p=False,
        related_name="secondary_groups")


####################
# Active Directory #
####################

class ad_person(methods.baseMixin):

    schema_list = [
        schemas.ad.person,
        schemas.rfc.organizationalPerson,
        schemas.rfc.inetOrgPerson,
        schemas.ad.user,
        schemas.ad.posixAccount,
    ]

    mixin_list = [
        methods.common.personMixin,
        methods.common.accountMixin,
        methods.ad.adUserMixin,
        PersonMixin,
    ]

    class Meta:
        base_dn_setting = "LDAP_PERSON_BASE"
        object_classes = {'top'}
        search_classes = {'user'}
        pk = 'cn'

    managed_by = tldap.manager.ManyToOneDescriptor(
        this_key='manager',
        linked_cls='karaage.datastores.ldap_schemas.ad_person',
        linked_key='dn')
    manager_of = tldap.manager.OneToManyDescriptor(
        this_key='dn',
        linked_cls='karaage.datastores.ldap_schemas.ad_person',
        linked_key='manager')


class ad_account(methods.baseMixin):

    schema_list = [
        schemas.ad.person,
        schemas.rfc.organizationalPerson,
        schemas.rfc.inetOrgPerson,
        schemas.ad.user,
        schemas.ad.posixAccount,
    ]

    mixin_list = [
        methods.common.personMixin,
        methods.common.accountMixin,
        methods.ad.adUserMixin,
        AccountMixin,
    ]

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = {'top'}
        search_classes = {'user'}
        pk = 'cn'

    managed_by = tldap.manager.ManyToOneDescriptor(
        this_key='manager',
        linked_cls='karaage.datastores.ldap_schemas.ad_account',
        linked_key='dn')
    manager_of = tldap.manager.OneToManyDescriptor(
        this_key='dn',
        linked_cls='karaage.datastores.ldap_schemas.ad_account',
        linked_key='manager')


class ad_person_group(methods.baseMixin):

    schema_list = [
        schemas.ad.group,
    ]

    mixin_list = [
        methods.ad.adGroupMixin,
    ]

    class Meta:
        base_dn_setting = "LDAP_GROUP_BASE"
        object_classes = {'top'}
        search_classes = {'group'}
        pk = 'cn'

    # accounts
    secondary_people = tldap.manager.AdAccountLinkDescriptor(
        linked_cls=ad_person, related_name="secondary_groups")


class ad_account_group(methods.baseMixin):

    schema_list = [
        schemas.rfc.posixGroup,
        schemas.ad.group,
    ]

    mixin_list = [
        methods.common.groupMixin,
        methods.ad.adGroupMixin
    ]

    class Meta:
        base_dn_setting = "LDAP_GROUP_BASE"
        object_classes = {'top'}
        search_classes = {'group'}
        pk = 'cn'

    # accounts
    primary_accounts = tldap.manager.OneToManyDescriptor(
        this_key='gidNumber',
        linked_cls=ad_account, linked_key='gidNumber',
        related_name="primary_group")
    secondary_accounts = tldap.manager.AdAccountLinkDescriptor(
        linked_cls=ad_account, related_name="secondary_groups")
