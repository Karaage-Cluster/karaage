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
from andsome.graphs.googlechart import GraphGenerator

from karaage.machines.models import MachineCategory
from karaage.institutes.models import Institute
from karaage.graphs import gen_project_graph, gen_institutes_trend
from karaage.graphs.util import smooth_data
from karaage.util.helpers import get_available_time

grapher = GraphGenerator()


def get_institute_graph_url(start, end, machine_category):

    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    try:
        open("%s/institutes/%s-%s_%i.png" % (settings.GRAPH_ROOT, start_str, end_str, machine_category.id))
    except IOError:
        institute_list = Institute.active.all()
        available_time, avg_cpus = get_available_time(start, end, machine_category)
        
        data = {}
        total = 0
        for i in institute_list:
            usage = i.get_usage(start, end, machine_category)
            if usage[0] is not None:
                total = total + float(usage[0])
                data[i.name] = float(usage[0])
            
        data['Unused'] = float(available_time - total)
        
        chart = grapher.pie_chart(data_dict=data)
        chart.download("%s/institutes/%s-%s_%i.png" % (settings.GRAPH_ROOT, start_str, end_str, machine_category.id))

    return "%sinstitutes/%s-%s_%i.png" % (settings.GRAPH_URL, start_str, end_str, machine_category.id)


def get_trend_graph_url(start, end, machine_category):

    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    try:
        open("%s/trends/trend_%i_%s-%s.png" % (settings.GRAPH_ROOT, machine_category.id, start_str, end_str))
    except IOError:
        
        mc_ids = tuple([(int(m.id)) for m in machine_category.machine_set.all()])
        if len(mc_ids) == 1:
            mc_ids = "(%i)" % mc_ids[0]

        cursor = connection.cursor()
        
        sql = "SELECT date, SUM( cpu_usage ) FROM `cpu_job` WHERE `machine_id` IN %s AND `date` >= '%s' AND `date` <= '%s' Group By date" % (mc_ids, start_str, end_str)
        cursor.execute(sql)
        rows = dict(cursor.fetchall())
        
        data, colours = smooth_data(rows, start, end)
    
        chart = grapher.sparkline(data)
        chart.download("%s/trends/trend_%i_%s-%s.png" % (settings.GRAPH_ROOT, machine_category.id, start_str, end_str))

    return "%strends/trend_%i_%s-%s.png" % (settings.GRAPH_URL, machine_category.id, start_str, end_str)


def get_institute_trend_graph_url(institute,
                                  start,
                                  end,
                                  machine_category):

    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    if settings.GRAPH_DEBUG:
        institute.gen_usage_graph(start, end, machine_category)

    try:
        open("%s/institutes/bar_%i_%s-%s_%i.png" % (settings.GRAPH_ROOT, institute.id, start_str, end_str, machine_category.id))
    except IOError:
        institute.gen_usage_graph(start, end, machine_category)
            
    return "bar_%i_%s-%s_%i.png" % (institute.id, start_str, end_str, machine_category.id)


def get_project_trend_graph_url(project,
                                start,
                                end,
                                machine_category):

    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    if settings.GRAPH_DEBUG:
        gen_project_graph(project, start, end, machine_category)

    try:
        open("%s/projects/%s_%s-%s_%i.png" % (settings.GRAPH_ROOT, project.pid, start_str, end_str, machine_category.id))
    except IOError:
        try:
            gen_project_graph(project, start, end, machine_category)
        except AssertionError:
            pass

    return "%s_%s-%s_%i.png" % (project.pid, start_str, end_str, machine_category.id)


def get_institutes_trend_graph_urls(start, end, machine_category):

    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    if settings.GRAPH_DEBUG:
        gen_institutes_trend(start, end, machine_category)

    try:
        for i in Institute.active.all():
            open("%s/i_trends/%s_%s_%s_%i-trend.png" % (settings.GRAPH_ROOT, i.name.replace(' ', '').replace('/', '-').lower(), start_str, end_str, machine_category.pk))
    except IOError:
        gen_institutes_trend(start, end, machine_category)

    graph_list = []
    for i in Institute.active.all():
        graph_list.append("%s_%s_%s_%i-trend.png" % (i.name.replace(' ', '').replace('/', '-').lower(), start_str, end_str, machine_category.pk))

    return graph_list
