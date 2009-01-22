#! /usr/bin/env python

"""

To Configure this program see alogger-ng.cfg

To customise this to read a different log format
just implement a method like pbs_to_dict (see below)

"""


import sys, os
import datetime

from karaage.machines.models import Machine, UserAccount
from karaage.usage.models import CPUJob, Queue
from karaage.projects.models import Project

from alogger_ng.utils import log_to_dict, get_in_seconds, print_error


DEBUG = False

    
"""
Assumes the file name is in the format YYYYMMDD

"""

def parse_logs(log_list, date, machine_name, log_type):
    """
    filename format YYYYMMDD
    
    """

    output = []
    count = fail = skip = updated = 0
    line_no = 0


    # Check things are setup correctly
    try:
        machine = Machine.objects.get(name=machine_name)
    except:
        return "ERROR: Couldn't find machine named: %s" % machine_name

    try:
        user_account = UserAccount.objects.get(username='unknown_user', machine_category=machine.category)
    except:
        return "ERROR: Couldn't find unknown_user for machine category %s, please create one" % machine.category.name

    try:
        project = Project.objects.get(pk='Unknown_Project')
    except:
        return "ERROR: Couldn't find project Unknown_Project, please create one"

    # Process each line  
  
    for line in log_list:
        line_no = line_no + 1
        try:
             data = log_to_dict(line, log_type)
        except ValueError:
            print_error(line_no, "Error reading line")
        except:
            skip = skip + 1
            continue

        try:
            user_account = UserAccount.objects.get(username=data['user'], machine_category=machine.category)
        except:
            # Couldn't find user account - Assign to user 'Unknown_User'
            user_account = UserAccount.objects.get(username='unknown_user', machine_category=machine.category)
            output.append("Couldn't find user account for username=%s and machine category=%s" % (data['user'], machine.category.name))
            fail = fail + 1



        if 'project' in data:
            try:
                project = Project.objects.get(pk=data['project'])
            except:
                try:
                    project = user_account.default_project
                except:
                    output.append(line_no, "Couldn't find specified project: %s" % data['project'])
                    project = Project.objects.get(pk='Unknown_Project')
                    fail = fail + 1

        else:
            try:
                project = user_account.default_project
            except:
                # Couldn't find project - Assign to 'Unknown_Project'
                output.append(line_no, "Couldn't find default project for username=%s and machine category=%s" % (data['user'], machine.category.name))
                project = Project.objects.get(pk='Unknown_Project')
                fail +=  1
                
        if project is None:
            project = Project.objects.get(pk='Unknown_Project')
        
        if user_account.user not in project.users.all():
            output.append(line_no, "%s is not in project %s, cpu usage: %s" % (user_account.user, project, data['cpu_usage']))
            fail += 1

        # Everything is good so add entry
        queue, created = Queue.objects.get_or_create(name=data['queue'])

        try:
            cpujob, created = CPUJob.objects.get_or_create(jobid=data['jobid'])

            cpujob.user=user_account
            cpujob.username=data['user']
            cpujob.project=project
            cpujob.machine=machine
            cpujob.date=date
            cpujob.queue=queue
            cpujob.cpu_usage=data['cpu_usage']
            cpujob.est_wall_time=data['est_wall_time']
            cpujob.act_wall_time=data['act_wall_time']
            cpujob.mem = data['mem']
            cpujob.vmem = data['vmem']
            cpujob.ctime = data['ctime']
            cpujob.qtime = data['qtime']
            cpujob.etime = data['etime']
            cpujob.start = data['start']
            cpujob.cores = data['cores']
            cpujob.exit_status = data['exit_status']
            cpujob.jobname = data['jobname']
            cpujob.list_mem = data['list_mem']
            cpujob.list_vmem = data['list_pmem']
            cpujob.list_pmem = data['list_vmem']
            cpujob.list_pvmem = data['list_pvmem']
            cpujob.save()
            
            if created:
                count += 1
            else:
                updated += 1
            
        except Exception, e:
            output.append("Failed to insert a line  - %s" % e)
            fail = fail + 1
            continue

    summary = 'Inserted : %i\nUpdated  : %i\nFailed   : %i\nSkiped   : %i' % (count, updated, fail, skip)


    if DEBUG:
        print 'Inserted : %i' % count
        print 'Updated  : %i' % updated
        print 'Failed   : %i' % fail
        print 'Skiped   : %i' % skip

        
    return summary, output

