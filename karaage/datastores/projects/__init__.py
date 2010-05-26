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

module = __import__(settings.PROJECT_DATASTORE, {}, {}, [''])

pds = module.ProjectDataStore()

def create_new_project(data):
    return pds.create_new_project(data)

def activate_project(project):
    return pds.activate_project(project)

def deactivate_project(project):
    pds.deactivate_project(project)

def add_user_to_project(person, project):
    pds.add_user_to_project(person, project)

def remove_user_from_project(person, project):
    pds.remove_user_from_project(person, project)

