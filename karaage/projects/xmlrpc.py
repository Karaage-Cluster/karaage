# Copyright 2007-2013 VPAC
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

from karaage.projects.models import Project
from karaage.machines.models import MachineCategory, Machine, Account
from karaage.util import log_object as log


def _get_machine_category(machine_name):
    """ Helper to make machine_name optional for backwards compatability. """
    if machine_name is None:
        # depreciated use
        machine_category = MachineCategory.objects.get_default()
    else:
        machine = Machine.objects.get(name=machine_name)
        machine_category = MachineCategory.objects.get(machine=machine)
    return machine_category


@xmlrpc_func(returns='list', args=['string'])
@permission_required(perm='projects.change_project')
def get_project_members(user, project_id):
    """
    Returns list of usernames given a project id
    """
    try:
        project = Project.objects.get(pid=project_id)
    except Project.DoesNotExist:
        return 'Project not found'
        
    return [x.user.username for x in project.group.members.all()]


@xmlrpc_func(returns='list')
@permission_required(perm='projects.change_project')
def get_projects(user):
    """
    Returns list of project ids
    """

    return [x.pid for x in Project.active.all()]


@xmlrpc_func(returns='string', args=['string', 'string', 'string'])
def get_project(username, proj, machine_name=None):
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
        return "User '%s' not found" % username
    if proj is None:
        project = account.default_project
    else:
        try:
            project = Project.objects.get(pid=proj)
        except Project.DoesNotExist:
            project = account.default_project
    if project:
        if account.person in project.group.members.all():
            return project.pid
        else:
            if account.person in account.default_project.group.members.all():
                return account.default_project.pid
            
    return "None"


@xmlrpc_func(returns='int', args=['string', 'string'])
@permission_required()
def change_default_project(user, project, machine_name=None):
    """
    Change default project
    """
    person = user
    try:
        project = Project.objects.get(pid=project)
    except Project.DoesNotExist:
        return -1, "Project %s does not exist" % project
    
    if not person in project.group.members.all():
        return -2, "User %s not a member of project %s" % (user, project.pid)
    
    machine_category = _get_machine_category(machine_name)
    account = Account.objects.get(
            username=username,
            machine_category=machine_category,
            date_deleted__isnull=True)
    
    account.default_project = project
    account.save()
    
    log(user.user, user, 2, 'Changed default project to %s' % project.pid)
    
    return 0, "Default project changed"


@xmlrpc_func(returns='list')
@permission_required()
def get_users_projects(user):
    """
    List projects a user is part of
    """
    person = user
    projects = person.projects.filter(is_active=True)
    return 0, [x.pid for x in projects]
