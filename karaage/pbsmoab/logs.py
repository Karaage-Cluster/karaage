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

from math import ceil

from karaage.machines.models import Machine, UserAccount
from karaage.usage.models import CPUJob, Queue
from karaage.projects.models import Project

from alogger import log_to_dict


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
    except Machine.DoesNotExist:
        return "ERROR: Couldn't find machine named: %s" % machine_name

    try:
        user_account = UserAccount.objects.get(username='unknown_user', machine_category=machine.category)
    except UserAccount.DoesNotExist:
        return "ERROR: Couldn't find unknown_user for machine category %s, please create one" % machine.category.name

    try:
        project = Project.objects.get(pk='Unknown_Project')
    except Project.DoesNotExist:
        return "ERROR: Couldn't find project Unknown_Project, please create one"

    # Process each line  
    for line in log_list:
        line_no = line_no + 1
        try:
             data = log_to_dict(line, log_type)
        except ValueError:
            output.append("Error reading line")
        except Exception, e:
            skip = skip + 1
            continue

        try:
            user_account = UserAccount.objects.get(username=data['user'], machine_category=machine.category, date_deleted__isnull=True)
        except UserAccount.DoesNotExist:
            # Couldn't find user account - Assign to user 'Unknown_User'
            user_account = UserAccount.objects.get(username='unknown_user', machine_category=machine.category)
            output.append("Couldn't find user account for username=%s and machine category=%s. Assigned to unknown user" % (data['user'], machine.category.name))
            fail = fail + 1
        except UserAccount.MultipleObjectsReturned:
            user_account = UserAccount.objects.get(username='unknown_user', machine_category=machine.category)
            output.append("Username %s has multiple active accounts on machine category %s. Assigned to unknown user" % (data['user'], machine.category.name))
            fail = fail + 1

        if 'project' in data:
            try:
                project = Project.objects.get(pk=data['project'])
            except Project.DoesNotExist:
                try:
                    project = user_account.default_project
                except:
                    output.append("Couldn't find specified project: %s" % data['project'])
                    project = Project.objects.get(pk='Unknown_Project')
                    fail = fail + 1

        else:
            try:
                project = user_account.default_project
            except:
                # Couldn't find project - Assign to 'Unknown_Project'
                output.append("Couldn't find default project for username=%s and machine category=%s" % (data['user'], machine.category.name))
                project = Project.objects.get(pk='Unknown_Project')
                fail +=  1
                
        if project is None:
            project = Project.objects.get(pk='Unknown_Project')
        
        if user_account.user not in project.users.all():
            output.append("%s is not in project %s, cpu usage: %s" % (user_account.user, project, data['cpu_usage']))
            fail += 1

        # Everything is good so add entry
        queue, created = Queue.objects.get_or_create(name=data['queue'])

        if machine.mem_per_core:
            avail_mem_per_core = machine.mem_per_core * 1024

            if data['list_pmem'] * data['cores'] > data['list_mem']:
                if data['list_pmem'] > avail_mem_per_core:
                    data['cpu_usage'] = ceil(data['list_pmem']/avail_mem_per_core * data['act_wall_time'] * data['cores'])
            else:
                if data['list_mem'] > avail_mem_per_core * data['cores']:
                    data['cpu_usage'] = ceil(data['list_pmem']/avail_mem_per_core * data['act_wall_time'])

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
            cpujob.list_vmem = data['list_vmem']
            cpujob.list_pmem = data['list_pmem']
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

