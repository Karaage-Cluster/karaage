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

from django.core.management.base import BaseCommand, CommandError

import tldap
import tldap.schemas.rfc
import tldap.transaction

import ldap.dn

class Command(BaseCommand):
    help = "Inititlise LDAP"
    args = "server [server ...]"

    def handle(self, *servers, **options):
        verbose = int(options.get('verbosity', 0))
        if len(servers) == 0:
            servers = "default",
        for server in servers:
            self._do_server(verbose, server)

    def _do_server(self, verbose, using):
        try:
            connection = tldap.connections[using]
        except KeyError:
            raise CommandError("LDAP Server %s not configured" % using)
        with tldap.transaction.commit_on_success(using=using):

            if verbose > 0:
                print "Processing %s" % using

            user_dn = connection.settings_dict['LDAP_ACCOUNT_BASE']
            group_dn = connection.settings_dict['LDAP_GROUP_BASE']

            user_base_dn = ldap.dn.dn2str(ldap.dn.str2dn(user_dn)[1:])
            group_base_dn = ldap.dn.dn2str(ldap.dn.str2dn(group_dn)[1:])

            ou = tldap.schemas.rfc.organizationalUnit
            v, c = ou.objects.using(using).base_dn(user_base_dn).get_or_create(dn=user_dn)
            if verbose > 0:
                if c:
                    print "Added " + user_dn
                else:
                    print user_dn + " already exists."

            v, c = ou.objects.using(using).base_dn(group_base_dn).get_or_create(dn=group_dn)
            if verbose > 0:
                if c:
                    print "Added " + group_dn
                else:
                    print group_dn + " already exists."
