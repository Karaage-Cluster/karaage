# Copyright 2015 VPAC
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

import json

from math import ceil
import logging

from karaage.machines.models import Machine, Account
from karaage.projects.models import Project

from alogger import get_parser

from .models import CPUJob, Queue

logger = logging.getLogger(__name__)

"""
Parse log files using alogger.
"""


class AloggerParser(object):

    def line_to_dict(self, line):
        return json.loads(line)


def parse_logs(log_list, date, machine_name, log_type):
    """
    Parse log file lines in log_type format.
    """
    output = []
    count = fail = skip = updated = 0

    # Check things are setup correctly
    try:
        machine = Machine.objects.get(name=machine_name)
    except Machine.DoesNotExist:
        return "ERROR: Couldn't find machine named: %s" % machine_name

    if log_type == "alogger":
        parser = AloggerParser()
    else:
        parser = get_parser(log_type)

    # Process each line
    for line_no, line in enumerate(log_list):
        try:
            data = parser.line_to_dict(line)
        except ValueError:
            output.append("%d: Error reading line" % line_no)
            continue

        # if parser returns None, nothing to do, continue to next line
        if data is None:
            skip += 1
            continue

        # check for required fields
        required_fields = [
            'user', 'project', 'jobid', 'jobname',
            'cpu_usage', 'cores',
            'act_wall_time', 'est_wall_time',
            'mem', 'vmem', 'list_pmem', 'list_mem', 'list_pvmem',
            'ctime', 'qtime', 'etime', 'start',
        ]

        for field in required_fields:
            if field not in data:
                output.append(
                    "line %d: %s field not given." % (line_no, field))
                fail = fail + 1
                continue

        # Process user --> account
        try:
            account = Account.objects.get(
                username=data['user'],
                machine_category=machine.category,
                date_deleted__isnull=True)

        except Account.DoesNotExist:
            # Couldn't find user account - Assign to user None
            output.append(
                "line %d: Couldn't find user account for username=%s and "
                "machine category=%s."
                % (line_no, data['user'], machine.category.name))
            fail += 1
            continue

        except Account.MultipleObjectsReturned:
            output.append(
                "line %d: Username %s has multiple active accounts on "
                "machine category %s."
                % (line_no, data['user'], machine.category.name))
            fail += 1
            continue

        # Process project
        if data['project'] is None:
            output.append(
                "line %d: Project was not supplied." % (line_no))
            fail += 1
            continue

        try:
            project = Project.objects.get(pid=data['project'])

        except Project.DoesNotExist:
            output.append(
                "line %d: Couldn't find specified project %s"
                % (line_no, data['project']))
            fail += 1
            continue

        # memory calculations
        if machine.mem_per_core:
            avail_mem_per_core = machine.mem_per_core * 1024
            avail_mem_for_job = avail_mem_per_core * data['cores']

            if data['list_pmem'] * data['cores'] > data['list_mem']:
                memory_used_per_core = data['list_pmem']
                memory_used_for_job = data['list_pmem'] * data['cores']
            else:
                memory_used_per_core = data['list_mem'] / data['cores']
                memory_used_for_job = data['list_mem']

            if memory_used_for_job > avail_mem_for_job:
                data['cpu_usage'] = ceil(
                    memory_used_per_core / avail_mem_per_core *
                    data['act_wall_time'] *
                    data['cores'])

        # apply scaling factor to cpu_usage
        data['cpu_usage'] = data['cpu_usage'] * machine.scaling_factor

        # Everything is good so add entry
        queue, created = Queue.objects.get_or_create(name=data['queue'])

        try:
            cpujob, created = CPUJob.objects.get_or_create(jobid=data['jobid'])
            cpujob.account = account
            cpujob.username = data['user']
            cpujob.project = project
            cpujob.machine = machine
            cpujob.date = date
            cpujob.queue = queue
            cpujob.cpu_usage = data['cpu_usage']
            cpujob.est_wall_time = data['est_wall_time']
            cpujob.act_wall_time = data['act_wall_time']
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

        except Exception as e:
            output.append(
                "line %d: Failed to insert a line  - %s" % (line_no, e))
            fail += 1
            continue

        if created:
            count += 1
        else:
            updated += 1

    summary = (
        'Inserted : %i\nUpdated  : %i\nFailed   : %i\nSkiped   : %i'
        % (count, updated, fail, skip)
    )

    logger.debug('Inserted : %i' % count)
    logger.debug('Updated  : %i' % updated)
    logger.debug('Failed   : %i' % fail)
    logger.debug('Skiped   : %i' % skip)

    return summary, output
