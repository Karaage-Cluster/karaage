# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
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

from django_xmlrpc.decorators import permission_required, xmlrpc_func

from karaage.common.decorators import xmlrpc_machine_required
from karaage.machines.models import Account
from karaage.projects.models import Project


@xmlrpc_machine_required()
@xmlrpc_func(returns='list', args=['string'])
def get_project_members(machine, project_id):
    """
    Returns list of usernames given a project id
    """
    try:
        project = Project.objects.get(pid=project_id)
    except Project.DoesNotExist:
        return 'Project not found'

    return [x.username for x in project.group.members.all()]


@xmlrpc_machine_required()
@xmlrpc_func(returns='list')
def get_projects(machine):
    """
    Returns list of project ids
    """

    query = Project.active.all()
    return [x.pid for x in query]


@xmlrpc_func(returns='string', args=['string', 'string', 'string'])
def get_project(username, project, machine_name=None):
    """
    Used in the submit filter to make sure user is in project
    """

    try:
        account = Account.objects.get(
            username=username,
            date_deleted__isnull=True)
    except Account.DoesNotExist:
        return "Account '%s' not found" % username

    if project is None:
        project = account.default_project
    else:
        try:
            project = Project.objects.get(pid=project)
        except Project.DoesNotExist:
            project = account.default_project

    if project is None:
        return "None"

    if account.person not in project.group.members.all():
        project = account.default_project

    if project is None:
        return "None"

    if account.person not in project.group.members.all():
        return "None"

    return project.pid


@permission_required()
@xmlrpc_func(returns='list')
def get_users_projects(user):
    """
    List projects a user is part of
    """
    person = user
    projects = person.projects.filter(is_active=True)
    return 0, [x.pid for x in projects]
