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

from django_xmlrpc.decorators import xmlrpc_func, permission_required
import datetime

from karaage.people.models import Person
from karaage.machines.models import MachineCategory, Account
from karaage.projects.models import Project
from karaage.pbsmoab.models import ProjectChunk
from karaage.pbsmoab.logs import parse_logs

@xmlrpc_func(returns='string', args=['string', 'date'])
@permission_required(perm='projects.change_project')
def parse_usage(user, usage, date, machine_name, log_type):
    """
    Parses usage
    """

    year, month, day = date.split('-')
    date = datetime.date(int(year), int(month), int(day))

    return parse_logs(usage, date, machine_name, log_type)



@xmlrpc_func(returns='boolean', args=['string'])
def project_under_quota(project_id):
    """
    Returns True if project is under quota
    """
    
    machine_category = MachineCategory.objects.get_default()
    try:
        project = Project.objects.get(pid=project_id)
    except Project.DoesNotExist:
        return 'Project not found'
        
    project_chunk, created = ProjectChunk.objects.get_or_create(project=project, machine_category=machine_category)

    if project_chunk.is_over_quota():
        return False
    
    return True


@xmlrpc_func(returns='int', args=['string'])
def get_disk_quota(username):
    """
    Returns disk quota for username in KB
    """

    machine_category = MachineCategory.objects.get_default()
    try:
        ua = Account.objects.get(user__user__username=username, machine_category=machine_category, date_deleted__isnull=True)
    except Account.DoesNotExist:
        return 'User account not found'
        
    return ua.get_disk_quota() * 1048576


@xmlrpc_func(returns='int, list', args=['string'])
def showquota(username):
    """
    returns a list a tuples
    (project_id, actual_mpots, quota_mpots)
    """
    machine_category = MachineCategory.objects.get_default()
    try:
        person = Person.active.get(user__username=username)
    except Person.DoesNotExist:
        return -1, 'User not found'
        
    try:
        u_a = person.get_account(machine_category)
        d_p = u_a.default_project
    except:
        return -1, 'Default Project not found'

    p_l = []
    for project in person.project_set.filter(is_active=True, machine_categories=machine_category):
        project_chunk, created = ProjectChunk.objects.get_or_create(project=project, machine_category=machine_category)
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



