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

from placard.client import LDAPClient
from placard.exceptions import DoesNotExistException

from karaage.datastores.software import base

class SoftwareDataStore(base.SoftwareDataStore):
    
    def create_software(self, software):  
        conn = LDAPClient()
        if software.gid:
             try:
                 lgroup = conn.get_group("gidNumber=%s" % software.gid)
                 gid = int(lgroup.gidNumber)
             except DoesNotExistException:
                 gid = conn.add_group(cn=str(software.name.lower().replace(' ', '')), gidNumber=str(software.gid))
        else:
                 
            try:
                lgroup = conn.get_group("cn=%s" % str(software.name.lower().replace(' ', '')))
                gid = int(lgroup.gidNumber)
            except DoesNotExistException:
                gid = conn.add_group(cn=str(software.name.lower().replace(' ', '')))

        del(conn)
        return gid

    def delete_software(self, software):
        conn = LDAPClient()
        try:
            conn.delete_group('cn=%s' % software.pid)
        except DoesNotExistException:
            pass
        del(conn)

    def add_member(self, software, person):
        conn = LDAPClient()
        conn.add_group_member('gidNumber=%s' % software.gid, str(person.username))
        del(conn)

    def remove_member(self, software, person):
        conn = LDAPClient()
        conn.remove_group_member('gidNumber=%s' % software.gid, str(person.username))
        del(conn)

        
    def get_members(self, software):
        conn = LDAPClient()
        try:
            return conn.get_group_members('gidNumber=%s' % software.gid)
        except:
            return []
        del(conn)

    def get_name(self, software):
        conn = LDAPClient()
        try:
            ldap_group = conn.get_group('gidNumber=%s' % software.gid)
            return ldap_group.cn
        except DoesNotExistException:
            return 'No LDAP Group'
