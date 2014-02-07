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

import tldap.schemas as schemas
import tldap.schemas.rfc
import tldap.schemas.ds389
import tldap.methods as methods
import tldap.methods.common
import tldap.methods.pwdpolicy
import tldap.methods.ds389
import tldap.manager

class kPersonMixin(object):
    @classmethod
    def pre_save(cls, self, using=None):
        # using parameter required for tldap 0.2.13 and earlier
        # delete when tldap 0.2.14 released.
        full_name = getattr(self, "fullName", None)
        self.displayName = u'%s (%s)' % (full_name, self.o)

class kAccountMixin(object):
    @classmethod
    def pre_save(cls, self, using=None):
        # using parameter required for tldap 0.2.13 and earlier
        # delete when tldap 0.2.14 released.
        full_name = getattr(self, "fullName", None)
        if full_name is None:
            full_name = "%s %s" % (self.givenName, self.sn)

        self.displayName = u'%s (%s)' % (full_name, self.o)
        self.gecos = u'%s (%s)' % (full_name, self.o)


############
# OpenLDAP #
############

class openldap_person(methods.baseMixin):

    schema_list = [
        schemas.rfc.person,
        schemas.rfc.organizationalPerson,
        schemas.rfc.inetOrgPerson,
        schemas.rfc.pwdPolicy,
        kPersonMixin,
    ]

    mixin_list = [
        methods.common.personMixin,
        methods.pwdpolicy.pwdPolicyMixin,
    ]

    class Meta:
        base_dn_setting = "LDAP_PERSON_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'person' ])
        pk = 'uid'

    managed_by = tldap.manager.ManyToOneDescriptor(this_key='manager', linked_cls='karaage.datastores.ldap_schemas.openldap_person', linked_key='dn')
    manager_of = tldap.manager.OneToManyDescriptor(this_key='dn', linked_cls='karaage.datastores.ldap_schemas.openldap_person', linked_key='manager')


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
        kAccountMixin,
    ]

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'person' ])
        # above is a hack required to upgrade to Karaage 3.0, should be the
        # following:
        # search_classes = set([ 'posixAccount' ])
        pk = 'uid'

    managed_by = tldap.manager.ManyToOneDescriptor(this_key='manager', linked_cls='karaage.datastores.ldap_schemas.openldap_account', linked_key='dn')
    manager_of = tldap.manager.OneToManyDescriptor(this_key='dn', linked_cls='karaage.datastores.ldap_schemas.openldap_account', linked_key='manager')
    unixHomeDirectory = tldap.manager.AliasDescriptor("homeDirectory")


class openldap_group(methods.baseMixin):

    schema_list = [ schemas.rfc.posixGroup ]
    mixin_list = [ methods.common.groupMixin ]

    class Meta:
        base_dn_setting = "LDAP_GROUP_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'posixGroup' ])
        pk = 'cn'

    # people
    secondary_people = tldap.manager.ManyToManyDescriptor(this_key='memberUid', linked_cls=openldap_person, linked_key='uid', linked_is_p=False, related_name="secondary_groups")

    # accounts
    primary_accounts = tldap.manager.OneToManyDescriptor(this_key='gidNumber', linked_cls=openldap_account, linked_key='gidNumber', related_name="primary_group")
    secondary_accounts = tldap.manager.ManyToManyDescriptor(this_key='memberUid', linked_cls=openldap_account, linked_key='uid', linked_is_p=False, related_name="secondary_groups")


############
# 389 LDAP #
############

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
        kPersonMixin,
    ]

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'person' ])
        pk = 'uid'

    managed_by = tldap.manager.ManyToOneDescriptor(this_key='manager', linked_cls='karaage.datastores.ldap_schemas.ds389_person', linked_key='dn')
    manager_of = tldap.manager.OneToManyDescriptor(this_key='dn', linked_cls='karaage.datastores.ldap_schemas.ds389_person', linked_key='manager')


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
        kAccountMixin,
    ]

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'person' ])
        # above is a hack required to upgrade to Karaage 3.0, should be the
        # following:
        # search_classes = set([ 'posixAccount' ])
        pk = 'uid'

    managed_by = tldap.manager.ManyToOneDescriptor(this_key='manager', linked_cls='karaage.datastores.ldap_schemas.ds389_account', linked_key='dn')
    manager_of = tldap.manager.OneToManyDescriptor(this_key='dn', linked_cls='karaage.datastores.ldap_schemas.ds389_account', linked_key='manager')
    unixHomeDirectory = tldap.manager.AliasDescriptor("homeDirectory")


class ds389_group(methods.baseMixin):

    schema_list = [ schemas.rfc.posixGroup ]
    mixin_list = [ methods.common.groupMixin ]

    class Meta:
        base_dn_setting = "LDAP_GROUP_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'posixGroup' ])
        pk = 'cn'

    # people
    secondary_people = tldap.manager.ManyToManyDescriptor(this_key='memberUid', linked_cls=ds389_person, linked_key='uid', linked_is_p=False, related_name="secondary_groups")


    # accounts
    primary_accounts = tldap.manager.OneToManyDescriptor(this_key='gidNumber', linked_cls=ds389_account, linked_key='gidNumber', related_name="primary_group")
    secondary_accounts = tldap.manager.ManyToManyDescriptor(this_key='memberUid', linked_cls=ds389_account, linked_key='uid', linked_is_p=False, related_name="secondary_groups")
