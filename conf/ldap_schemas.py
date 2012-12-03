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

from tldap.schemas import rfc
from placard.schemas import common
from placard.schemas.pwdpolicy import pwdPolicyMixin
import tldap.manager
import django.conf
import time
import datetime

import placard.ldap_passwd

##########
# person #
##########

class kPersonMixin(object):
    def prepare_for_save(self, *args, **kwargs):
        self.displayName = '%s %s (%s)' % (self.givenName, self.sn, self.o)

class person(rfc.person, rfc.organizationalPerson, rfc.inetOrgPerson, rfc.pwdPolicy, common.baseMixin):
    mixin_list = [ common.personMixin, pwdPolicyMixin, kPersonMixin ]

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'person' ])
        pk = 'uid'

    managed_by = tldap.manager.ManyToOneDescriptor('manager', 'karaage.datastores.ldap_models.person', 'dn')
    manager_of = tldap.manager.OneToManyDescriptor('dn', 'karaage.datastores.ldap_models.person', 'manager')


###########
# account #
###########

class account(person, rfc.posixAccount, rfc.shadowAccount):
    mixin_list = person.mixin_list + [ common.accountMixin ]

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'posixAccount' ])
        pk = 'uid'

    managed_by = tldap.manager.ManyToOneDescriptor('manager', 'karaage.datastores.ldap_models.account', 'dn')
    manager_of = tldap.manager.OneToManyDescriptor('dn', 'karaage.datastores.ldap_models.account', 'manager')
    unixHomeDirectory = tldap.manager.AliasDescriptor("homeDirectory")

#########
# group #
#########

class group(rfc.posixGroup, common.baseMixin):
    mixin_list = [ common.groupMixin ]

    class Meta:
        base_dn_setting = "LDAP_GROUP_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'posixGroup' ])
        pk = 'cn'

    # accounts
    primary_accounts = tldap.manager.OneToManyDescriptor('gidNumber', account, 'gidNumber', "primary_group")
    secondary_accounts = tldap.manager.ManyToManyDescriptor('memberUid', account, 'uid', False, "secondary_groups")
