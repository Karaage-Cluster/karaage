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

from karaage.datastores import ldap_schemas

from karaage.datastores.software import base


class SoftwareDataStore(base.SoftwareDataStore):
    
    def create_software(self, software):
        if software.gid:
            try:
                lgroup = ldap_schemas.group.objects.get(gidNumber=software.gid)
            except DoesNotExistException:
                lgroup = ldap_schemas.group(cn=str(software.name.lower().replace(' ', '')), gidNumber=str(software.gid))
                lgroup.set_defaults()
                lgroup.pre_create(master=None)
                lgroup.pre_save()
                lgroup.save()
        else:
            if not software.restricted and software.softwarelicense_set.count() == 0:
                return None
            try:
                lgroup = ldap_schemas.group.objects.get(cn=str(software.name.lower().replace(' ', '')))
            except ldap_schemas.group.DoesNotExist:
                lgroup = ldap_schemas.group(cn=str(software.name.lower().replace(' ', '')))
                lgroup.set_defaults()
                lgroup.pre_create(master=None)
                lgroup.pre_save()
                lgroup.save()

        assert lgroup.gidNumber is not None
        return lgroup.gidNumber

    def delete_software(self, software):
        if software.gid is None:
            return

        try:
            lgroup = ldap_schemas.group.objects.get(gidNumber=software.gid)
            lgroup.delete()
        except ldap_schemas.group.DoesNotExist:
            return

    def add_member(self, software, person):
        lgroup = ldap_schemas.group.objects.get(gidNumber=software.gid)
        person = ldap_schemas.person.objects.get(uid=person.username)
        lgroup.secondary_persons.add(person)

    def remove_member(self, software, person):
        lgroup = ldap_schemas.group.objects.get(gidNumber=software.gid)
        person = ldap_schemas.person.objects.get(uid=person.username)
        lgroup.secondary_persons.remove(person)

    def get_members(self, software):
        if software.gid is not None:
            lgroup = ldap_schemas.group.objects.get(gidNumber=software.gid)
            return lgroup.secondary_persons.all()
        else:
            return []

    def get_name(self, software):
        if software.gid is not None:
            lgroup = ldap_schemas.group.objects.get(gidNumber=software.gid)
            return lgroup.cn
        else:
            return 'No LDAP Group'
