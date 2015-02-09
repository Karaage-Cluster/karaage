# Copyright 2011-2015 VPAC
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

from django_xmlrpc.decorators import xmlrpc_func, permission_required

from karaage.projects.models import Project, ProjectQuota
from karaage.machines.models import MachineCategory, Machine, Account
from karaage.common.decorators import xmlrpc_machine_required


def _get_machine_category(machine_name):
    """ Helper to make machine_name optional for backwards compatability. """
    if machine_name is None:
        # depreciated use
        machine_category = MachineCategory.objects.get_default()
    else:
        machine = Machine.objects.get(name=machine_name)
        machine_category = MachineCategory.objects.get(machine=machine)
    return machine_category


@xmlrpc_machine_required()
@xmlrpc_func(returns='list', args=['string'])
def get_project_members(machine, project_id):
    """
    Returns list of usernames given a project id
    """
    try:
        project = Project.objects.get(
            pid=project_id, projectquota__machine_category=machine.category)
    except Project.DoesNotExist:
        return 'Project not found'

    return [x.username for x in project.group.members.all()]


@xmlrpc_machine_required()
@xmlrpc_func(returns='list')
def get_projects(machine):
    """
    Returns list of project ids
    """

    query = Project.active.filter(
        projectquota__machine_category=machine.category)
    return [x.pid for x in query]


@xmlrpc_func(returns='string', args=['string', 'string', 'string'])
def get_project(username, project, machine_name=None):
    """
    Used in the submit filter to make sure user is in project
    """

    machine_category = _get_machine_category(machine_name)
    try:
        account = Account.objects.get(
            username=username,
            machine_category=machine_category,
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


@xmlrpc_func(returns='int, list', args=['string', 'string'])
def showquota(username, machine_name=None):
    """
    returns a list a tuples
    (project_id, actual_mpots, quota_mpots)
    """

    machine_category = _get_machine_category(machine_name)

    try:
        u_a = Account.objects.get(
            username=username,
            machine_category=machine_category,
            date_deleted__isnull=True)
    except Account.DoesNotExist:
        return -1, 'Account not found'

    d_p = u_a.default_project
    if d_p is None:
        return -1, 'Default Project not set'

    p_l = []
    query = ProjectQuota.objects.filter(
        project__is_active=True, machine_category=machine_category)
    for project_chunk in query:
        project = project_chunk.project

        is_default = False
        if project == d_p:
            is_default = True

        # Is this needed?
        mpots = 0

        cap = str(float(project_chunk.get_cap()))

        p_l.append([
            project.pid,
            mpots,
            cap,
            is_default,
        ])

    return 0, p_l
