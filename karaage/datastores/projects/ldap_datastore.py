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
    
    def create_new_project(self, data):
        project = super(ProjectDataStore, self).create_new_project(data)
        conn = LDAPClient()
        conn.add_group(cn=str(project.pid))
        return project

    def activate_project(self, project):
        project = super(ProjectDataStore, self).activate_project(project)
        return project

    def deactivate_project(self, project):
        super(ProjectDataStore, self).deactivate_project(project)

    def add_user_to_project(self, person, project):
        super(ProjectDataStore, self).add_user_to_project(person, project)
        
        conn = LDAPClient()
        conn.add_group_member('cn=%s' % project.pid, person.username)

    def remove_user_from_project(self, person, project):
        super(ProjectDataStore, self).remove_user_from_project(person, project)
        
        conn = LDAPClient()
        conn.remove_group_member('cn=%s' % project.pid, person.username)
