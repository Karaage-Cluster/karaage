from django.core import serializers
from django.shortcuts import get_object_or_404

from django_xmlrpc.decorators import xmlrpc_func, permission_required

from karaage.people.models import Person
from karaage.machines.models import MachineCategory, UserAccount
from karaage.projects.models import Project

from models import ProjectChunk

@xmlrpc_func(returns='string', args=['string', 'string'])
def get_project(username, proj=None):
    """
    Used in the submit filter to make sure user is in project
    """
    
    try:
        user_account = UserAccount.objects.get(username=username,machine_category=MachineCategory.objects.get_default())
    except:
        return "User '%s' not found" % username
    if proj is None:
        return user_account.default_project.pid
    else:
        try:
            project = Project.objects.get(pid=proj)
        except:
            return user_account.default_project.pid
        
    
        if user_account.user in project.users.all():
            return project.pid
        else:
            return user_account.default_project.pid


@xmlrpc_func(returns='boolean', args=['string'])
def project_under_quota(project_id):
    """
    Returns True if project is under quota
    """
    
 
    try:
        project = Project.objects.get(pid=project_id)
    except:
        return 'Project not found'
        
    project_chunk, created = ProjectChunk.objects.get_or_create(project=project)

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
        ua = UserAccount.objects.get(user__user__username=username, machine_category=machine_category, date_deleted__isnull=True)
    except:
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
    except:
        return -1, 'User not found'
        
    try:
        u_a = person.get_user_account(machine_category)
        d_p = u_a.default_project
    except:
        return -1, 'Default Project not found'

    p_l = []
    for project in person.project_set.filter(is_active=True):
        project_chunk, created = ProjectChunk.objects.get_or_create(project=project)
        is_default = False
        if project == d_p:
            is_default = True
        p_l.append([
                project.pid, 
                str(float(project_chunk.get_mpots())), 
                str(float(project_chunk.get_cap())),
                is_default,
                ])


    return 0, p_l
