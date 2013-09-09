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

from django.conf import settings

module = __import__(settings.SOFTWARE_DATASTORE, {}, {}, [''])
pds = module.SoftwareDataStore()


def create_software(software):
    return pds.create_software(software)


def delete_software(software):
    return pds.delete_software(software)


def add_member(software, person):
    return pds.add_member(software, person)


def remove_member(software, person):
    return pds.remove_member(software, person)


def get_members(software):
    return pds.get_members(software)


def get_name(software):
    return pds.get_name(software)
