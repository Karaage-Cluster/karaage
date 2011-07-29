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

from django.conf import settings
from django.db import connection

import datetime

from karaage.machines.models import MachineCategory


def smooth_data(rows, start, end):

    today = datetime.date.today()
    data = []
    colours = []
    period = (end - start).days
    
    if period >= 3000:
        while start <= end:
            start_e = start
            if start != today:
                total = 0
                
                end_e = start_e + datetime.timedelta(days=15)
                while start_e <= end_e:
                    try:
                        add = rows[start_e]
                    except:
                        add = 0
                    total = total + add
                    start_e= start_e  + datetime.timedelta(days=1)

                total = total / 3600  
                data.append(float(total))
                colours.append(0x9AB8D7)
            start = start + datetime.timedelta(days=15)
    elif period >= 300:
        while start <= end:
            start_e = start
            if start != today:
                total = 0
                
                end_e = start_e + datetime.timedelta(days=5)
                while start_e <= end_e:
                    try:
                        add = rows[start_e]
                    except:
                        add = 0
                    total = total + add
                    start_e= start_e  + datetime.timedelta(days=1)

                total = total / 3600  
                data.append(float(total))
                colours.append(0x9AB8D7)
            start = start + datetime.timedelta(days=5)
    else:
        while start <= end:
            if start != today:
                try:
                    total = int(rows[start])
                except:
                    total = 0
                total = total / 3600  
                data.append(float(total))
                colours.append(0x9AB8D7)
            start = start + datetime.timedelta(days=1)

    
    return data, colours


def get_insitutes_trend(institute, start, end, machine_category=MachineCategory.objects.get(pk=settings.DEFAULT_MC)):
    if institute.project_set.count() == 0 or machine_category.machine_set.count() == 0:
        return []
    project_ids = tuple([str((p.pid)) for p in institute.project_set.all()])
    if len(project_ids) == 1:
        project_ids = "('%s')" % str(project_ids[0])

    if not project_ids:
        return {}
    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    period = (end - start).days

    mc_ids = tuple([(int(m.id)) for m in machine_category.machine_set.all()])
    if len(mc_ids) == 1:
        mc_ids = "(%i)" % mc_ids[0]

    cursor = connection.cursor()
    SQL = "SELECT date, SUM( cpu_usage ) FROM `cpu_job` WHERE `project_id` IN %s AND `machine_id` IN %s AND `date` >= '%s' AND `date` <= '%s' Group By date" % (project_ids, mc_ids, start_str, end_str)
    cursor.execute(SQL)
    rows = dict(cursor.fetchall())
    return rows



def get_colour(index):
    colours = ['red','blue','green','pink', 'yellow', 'magenta','orange', 'cyan',]
    default_colour = 'purple'
    try:
        return colours[index]
    except:
        return default_colour
