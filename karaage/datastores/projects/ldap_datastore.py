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

from karaage.datastores.projects import base


class ProjectDataStore(base.ProjectDataStore):
    
    def create_or_update_project(self, project):
        conn = LDAPClient()
        try:
            lgroup = conn.get_group('cn=%s' % project.pid)
        except:
            conn.add_group(cn=str(project.pid))
        users = [str(person.user.username) for person in project.users.all()]
        conn.update_group('cn=%s' % project.pid, memberUid=users)

    def delete_project(self, project):
        conn = LDAPClient()
        conn.delete_group('cn=%s' % project.pid)


