"""
Methods for getting usage data
uses a database cache to speed up proccess

"""
__author__ = 'Sam Morrison'
from django.db import connection

import datetime

from karaage.cache.models import InstituteCache, ProjectCache, UserCache, MachineCache
from karaage.usage.models import CPUJob
from karaage.machines.models import UserAccount

def get_instititue_usage_period(institute, period, machine_category):
    """Return a tuple of cpu hours and number of jobs for an institute

    Keyword arguments:
    institute -- 
    period -- number of days back from today
    machine_category -- MachineCategory object
    
    """
    end = datetime.date.today()
    start = end - datetime.timedelta(days=int(period))
    return get_institute_usage_date(institute, start, end, machine_category)

def get_institute_usage(institute, start, end, machine_category):
    """Return a tuple of cpu hours and number of jobs for an institute
    for a given period

    Keyword arguments:
    institute -- 
    start -- start date
    end -- end date
    machine_category -- MachineCategory object
    
    """
    try:
        cache = InstituteCache.objects.get(institute=institute, date=datetime.date.today(), start=start, end=end, machine_category=machine_category)
    except:
        pids = tuple([( str(p.pid))for p in institute.project_set.all()])
        mc_ids = tuple([(int(m.id)) for m in machine_category.machine_set.all()])

        if len(mc_ids) == 1:
            mc_ids = "(%i)" % mc_ids[0]
        if len(pids) == 1:
            pids = "('%s')" % str(pids[0])

        
        start_str = start.strftime('%Y-%m-%d')
        end_str = end.strftime('%Y-%m-%d')
        
        if len(pids) == 0:
            return 0,0
        cursor = connection.cursor()
        SQL = "SELECT SUM(cpu_usage), COUNT(*) FROM cpu_job WHERE project_id IN %s AND machine_id IN %s AND date >= '%s' AND `date` <= '%s'" % (pids, mc_ids, start_str, end_str)
        cursor.execute(SQL)
        row = cursor.fetchone()
        cache = InstituteCache.objects.create(institute=institute, start=start, end=end, machine_category=machine_category, cpu_hours=row[0], no_jobs=row[1])
    return cache.cpu_hours, cache.no_jobs


def get_project_usage_period(project, period):
    """Return a tuple of cpu hours and number of jobs for a project

    Keyword arguments:
    project -- 
    period -- number of days back from today
    
    """
    end = datetime.date.today()
    start = end - datetime.timedelta(days=int(period))
    return get_project_usage_date(project, start, end)


def get_project_usage(project, start, end):
    """Return a tuple of cpu hours and number of jobs for a project
    for a given period

    Keyword arguments:
    project -- 
    start -- start date
    end -- end date
    
    """
    if project.machine_categories.count() == 1:
        machine_category = project.machine_categories.all()[0]
    else:
        machine_category = project.machine_category
    try:
        cache = ProjectCache.objects.get(pid=project, date=datetime.date.today(), start=start, end=end, machine_category=machine_category)
    except:
        
        start_str = start.strftime('%Y-%m-%d')
        end_str = end.strftime('%Y-%m-%d')
        
        mc_ids = tuple([(int(m.id)) for m in machine_category.machine_set.all()])
        if len(mc_ids) == 1:
            mc_ids = "(%i)" % mc_ids[0]
            
        cursor = connection.cursor()
        SQL = "SELECT SUM( cpu_usage ) , COUNT( * ) FROM `cpu_job` WHERE `project_id` LIKE '%s' AND machine_id IN %s AND `date` >= '%s' AND `date` <= '%s'" % (str(project.pid), mc_ids, start_str, end_str)
        cursor.execute(SQL)
        row = cursor.fetchone()
        cache =  ProjectCache.objects.create(pid=project, start=start, end=end, machine_category=machine_category, cpu_hours=row[0], no_jobs=row[1])
    return cache.cpu_hours, cache.no_jobs


def get_user_usage_period(user, project, period):
    """Return a tuple of cpu hours and number of jobs for a user in a specific project

    Keyword arguments:
    user -- 
    project -- The project the usage is from 
    period -- number of days back from today  
    """
    end = datetime.date.today()
    start = end - datetime.timedelta(days=int(period))
    return get_user_usage_date(project, start, end)


def get_user_usage(user, project, start, end):
    """Return a tuple of cpu hours and number of jobs for a user in a specific project

    Keyword arguments:
    user -- 
    project -- The project the usage is from
    start -- start date
    end -- end date 
    """
    try:
        cache = UserCache.objects.get(user=user, project=project, date=datetime.date.today(), start=start, end=end)
    except:
        total_usage = total_jobs = 0
        accounts = UserAccount.objects.filter(user=user)

        usage = CPUJob.objects.filter(date__range=(start, end)).filter(project=project).filter(user__in=accounts)
        for u in usage:
            total_usage = total_usage + u.cpu_usage
            total_jobs = total_jobs + 1

        cache = UserCache.objects.create(user=user, project=project, start=start, end=end, cpu_hours=total_usage, no_jobs=total_jobs)

    return cache.cpu_hours, cache.no_jobs



def get_machine_usage(machine, start, end):
    """Return a tuple of cpu hours and number of jobs for a machine
    for a given period

    Keyword arguments:
    machine -- 
    start -- start date
    end -- end date
    
    """
    
    try:
        cache = MachineCache.objects.get(machine=machine, date=datetime.date.today(), start=start, end=end)
    except:
        
        start_str = start.strftime('%Y-%m-%d')
        end_str = end.strftime('%Y-%m-%d')
  
        cursor = connection.cursor()
        SQL = "SELECT SUM(cpu_usage), COUNT(*) FROM cpu_job WHERE machine_id LIKE '%s' AND date >= '%s' AND date <= '%s'" % (str(machine.id), start_str, end_str)
        cursor.execute(SQL)
        row = cursor.fetchone()
        cache =  MachineCache.objects.create(machine=machine, start=start, end=end, cpu_hours=row[0], no_jobs=row[1])

    return cache.cpu_hours, cache.no_jobs

