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

from __future__ import absolute_import

from math import ceil

from karaage.machines.models import Machine, Account
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
            account = Account.objects.get(username=data['user'], machine_category=machine.category, date_deleted__isnull=True)
        except Account.DoesNotExist:
            # Couldn't find user account - Assign to user None
            account = None
            output.append("Couldn't find user account for username=%s and machine category=%s. Assigned to None" % (data['user'], machine.category.name))
            fail = fail + 1
        except Account.MultipleObjectsReturned:
            account = None
            output.append("Username %s has multiple active accounts on machine category %s. Assigned to None" % (data['user'], machine.category.name))
            fail = fail + 1

        if 'project' in data:
            try:
                project = Project.objects.get(pid=data['project'])
            except Project.DoesNotExist:
                output.append("Couldn't find specified project %s, using default project" % data['project'])
                fail = fail + 1

                try:
                    project = account.default_project
                except:
                    output.append("Couldn't find default project %s, using None" % account.default_project)
                    project = None

        else:
            try:
                project = account.default_project
            except:
                # Couldn't find project - Assign to None
                output.append("Couldn't find default project for username=%s and machine category=%s" % (data['user'], machine.category.name))
                project = None
                fail +=  1
                
        if project is not None and account is not None:
        
            if account.user not in project.users.all():
                output.append("%s is not in project %s, cpu usage: %s" % (account.user, project, data['cpu_usage']))
                fail += 1

        # Everything is good so add entry
        queue, created = Queue.objects.get_or_create(name=data['queue'])

        if machine.mem_per_core:
            avail_mem_per_core = machine.mem_per_core * 1024
            avail_mem_for_job  = avail_mem_per_core * data['cores']

            if data['list_pmem'] * data['cores'] > data['list_mem']:
                memory_used_per_core = data['list_pmem']
                memory_used_for_job  = data['list_pmem'] * data['cores']
            else:
                memory_used_per_core = data['list_mem'] / data['cores']
                memory_used_for_job = data['list_mem']

            if memory_used_for_job > avail_mem_for_job:
                data['cpu_usage'] = ceil(memory_used_per_core/avail_mem_per_core * data['act_wall_time'] * data['cores'])

        data['cpu_usage'] = data['cpu_usage'] * machine.scaling_factor

        try:
            cpujob, created = CPUJob.objects.get_or_create(jobid=data['jobid'])
            cpujob.user=account
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

