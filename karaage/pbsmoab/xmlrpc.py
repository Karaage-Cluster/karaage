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
import datetime

from karaage.people.models import Person
from karaage.machines.models import MachineCategory, Machine, Account
from karaage.projects.models import Project, ProjectQuota
from karaage.pbsmoab.logs import parse_logs


def _get_machine_category(machine_name):
    """ Helper to make machine_name optional for backwards compatability. """
    if machine_name is None:
        # depreciated use
        machine_category = MachineCategory.objects.get_default()
    else:
        machine = Machine.objects.get(name=machine_name)
        machine_category = MachineCategory.objects.get(machine=machine)
    return machine_category


@xmlrpc_func(returns='string', args=['string', 'date'])
@permission_required(perm='projects.change_project')
def parse_usage(user, usage, date, machine_name, log_type):
    """
    Parses usage
    """

    year, month, day = date.split('-')
    date = datetime.date(int(year), int(month), int(day))

    return parse_logs(usage, date, machine_name, log_type)


@xmlrpc_func(returns='boolean', args=['string', 'string'])
def project_under_quota(project_id, machine_name=None):
    """
    Returns True if project is under quota
    """
    
    machine_category = _get_machine_category(machine_name)
    try:
        project = Project.objects.get(pid=project_id)
    except Project.DoesNotExist:
        return 'Project not found'
        
    project_chunk, created = ProjectQuota.objects.get_or_create(project=project, machine_category=machine_category)

    if project_chunk.is_over_quota():
        return False
    
    return True


@xmlrpc_func(returns='int', args=['string', 'string'])
def get_disk_quota(username, machine_name=None):
    """
    Returns disk quota for username in KB
    """

    machine_category = _get_machine_category(machine_name)
    try:
        ua = Account.objects.get(
                username=username,
                machine_category=machine_category,
                date_deleted__isnull=True)
    except Account.DoesNotExist:
        return 'User account not found'
        
    return ua.get_disk_quota() * 1048576


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
    except:
        return -1, 'Account not found'

    try:
        d_p = u_a.default_project
    except:
        return -1, 'Default Project not found'

    p_l = []
    for project in u_a.person.projects.filter(is_active=True, machine_categories=machine_category):
        project_chunk, created = ProjectQuota.objects.get_or_create(project=project, machine_category=machine_category)
        is_default = False
        if project == d_p:
            is_default = True


        try:
            mpots = str(float(project_chunk.get_mpots()))
        except:
            mpots = 0

        try:
            cap = str(float(project_chunk.get_cap()))
        except:
            cap = 0

        p_l.append([
                project.pid, 
                mpots,
                cap,
                is_default,
                ])


    return 0, p_l



