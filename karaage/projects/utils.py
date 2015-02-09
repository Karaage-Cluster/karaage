# Copyright 2009-2013, 2015 VPAC
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

from karaage.projects.models import Project
from karaage.machines.models import Account


def add_user_to_project(person, project):
    for pc in project.projectquota_set.all():
        if not person.has_account(pc.machine_category):
            Account.create(person, project, pc.machine_category)
    project.group.members.add(person)


def remove_user_from_project(person, project):
    project.group.members.remove(person)


def get_new_pid(institute):
    """ Return a new Project ID
    Keyword arguments:
    institute_id -- Institute id
    """
    number = '0001'
    prefix = 'p%s' % institute.name.replace(' ', '')[:4]

    found = True
    while found:
        try:
            Project.objects.get(pid=prefix + number)
            number = str(int(number) + 1)
            if len(number) == 1:
                number = '000' + number
            elif len(number) == 2:
                number = '00' + number
            elif len(number) == 3:
                number = '0' + number
        except Project.DoesNotExist:
            found = False

    return prefix + number
