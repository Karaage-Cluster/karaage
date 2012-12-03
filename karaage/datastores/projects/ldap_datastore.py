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

from karaage.datastores.projects import base
from karaage.datastores import ldap_schemas

class ProjectDataStore(base.ProjectDataStore):

    def create_or_update_project(self, project):
        try:
            group = ldap_schemas.group.objects.get(cn=project.pid)
        except ldap_schemas.group.DoesNotExist:
            group = ldap_schemas.group(cn=project.pid)
            group.set_defaults()
        group.secondary_accounts.clear(commit=False)
        for person in project.users.all():
            luser = ldap_schemas.account.objects.get(uid=person.user.username)
            group.secondary_accounts.add(luser, commit=False)
        group.save()

    def delete_project(self, project):
        group = ldap_schemas.group.objects.get(cn=project.pid)
        group.delete()
