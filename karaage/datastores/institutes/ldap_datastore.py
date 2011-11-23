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
from karaage.datastores.institutes import base


class InstituteDataStore(base.InstituteDataStore):
    
    def create_institute(self, institute):
        conn = LDAPClient()
        if institute.gid:
            try:
                lgroup = conn.get_group("gidNumber=%s" % institute.gid)
                gid = int(lgroup.gidNumber)
            except DoesNotExistException:
                gid = conn.add_group(cn=str(institute.name.lower().replace(' ', '')), gidNumber=str(institute.gid))
        else:
                 
            try:
                lgroup = conn.get_group("cn=%s" % str(institute.name.lower().replace(' ', '')))
                gid = int(lgroup.gidNumber)
            except DoesNotExistException:
                gid = conn.add_group(cn=str(institute.name.lower().replace(' ', '')))
        del(conn)
        return gid

    def delete_institute(self, institute):
        conn = LDAPClient()
        try:
            conn.delete_group('cn=%s' % institute.gid)
        except DoesNotExistException:
            pass
