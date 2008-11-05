"""
Graph generation using gdchart2
"""

from django.conf import settings
from django.db import connection

import gdchart
import datetime

from karaage.people.models import Institute
from karaage.machines.models import MachineCategory
from karaage.projects.models import Project
from karaage.usage.models import CPUJob
from karaage.util.helpers import get_available_time

import base
from util import *

__author__ = 'Sam Morrison'


class GraphGenerator(base.GraphGenerator):

    def gen_project_graph(self, project, start, end, machine_category):
        """Generates a bar graph for a project
    
        Keyword arguments:
        project -- Project
        start -- start date
        end -- end date
        machine_category -- MachineCategory object
    
        """

        start_str = start.strftime('%Y-%m-%d')
        end_str = end.strftime('%Y-%m-%d')

        x = gdchart.Bar()
        x.width = 700
        x.height = 350
        x.bg_color = "white"
        x.xtitle = "Days"
        x.ytitle = "CPU Time (hours)"
        x.title = '%s - %s-%s' % (project.pid, start_str, end_str)
        x.grid = "NONE"
        
        today = datetime.date.today()
        
        mc_ids = tuple([(int(m.id)) for m in machine_category.machine_set.all()])
        if len(mc_ids) == 1:
            mc_ids = "(%i)" % mc_ids[0]

        cursor = connection.cursor()
        SQL = "SELECT date, SUM( cpu_usage ) FROM `cpu_job` WHERE `project_id` LIKE '%s' AND `machine_id` IN %s AND `date` >= '%s' AND `date` <= '%s' Group By date" % (str(project.pid), mc_ids, start_str, end_str)
        cursor.execute(SQL)
        rows = dict(cursor.fetchall())
        

        labels, data, colours = [], [], []
        while start <= end:
            if start != today:
                try:
                    total = int(rows[start])
                except:
                    total = 0
                total = total / 3600  
                data.append(total)
                colours.append(0x9AB8D7)
            start = start + datetime.timedelta(days=1)

        x.ext_color = colours
        x.setData(data)
        try:
            x.draw("%s/graphs/projects/%s_%s-%s_%i.png" % (settings.MEDIA_ROOT, project.pid, start_str, end_str, machine_category.id))

        except:
            pass



    def gen_institutes_pie(self, start, end, machine_category):
        """Generates a pie graph showing all primary institutes usage
    
        Keyword arguments:
        start -- start date
        end -- end date
        machine_category -- MachineCategory object
        
        """
        today = datetime.date.today()
        
        start_str = start.strftime('%Y-%m-%d')
        end_str = end.strftime('%Y-%m-%d')
        
        institute_list = Institute.primary.all()
        
        available_time, avg_cpus = get_available_time(start, end, machine_category)
        
        myPie = gdchart.Pie()
        myPie.width = 500
        myPie.height = 500
        myPie.title = "Institutes Usage - (%s - %s) - %s" % (start_str, end_str, machine_category.name) 
        myPie.bg_color = "white"
        data = []
        i_list = []
        labels = []
        total = 0
        for i in institute_list:  
            usage = i.get_usage(start, end, machine_category)
            if usage[0] is not None:
                total = total + int(usage[0])
                data.append(int(usage[0]))
                labels.append(i.name)

        data.append(int(available_time - total))
        labels.append('Unused')
        data = tuple(data)
        
        myPie._datalen = len(data)
        myPie._data = data
        myPie._conformanceCheck()
        
        myPie.setLabels(labels)
        
        #myPie.explode = [10,10,10,10,10,10,10,10,10,10]

        myPie.color = ["red", "green", "yellow", "orange", "blue", "red", "green", "yellow", "orange", "blue"]

        try:
            myPie.draw("%s/graphs/institutes/%s-%s_%i.png" % (settings.MEDIA_ROOT, start_str, end_str, machine_category.id))
        except:
            pass
    

    def gen_quota_graph(self):
        """Generates a pie graph for all primary institutes quota       
        """
        institute_list = Institute.primary.all()
    
        myPie = gdchart.Pie()
        myPie.width = 500
        myPie.height = 500
        myPie.title = "Institutes Quota"
        myPie.bg_color = "white"
        data = []
        i_list = []
        labels = []
        for i in institute_list:  
            data.append(int(i.quota))
            labels.append(i.name)
            
        data = tuple(data)
        
        myPie._datalen = len(data)
        myPie._data = data
        myPie._conformanceCheck()
        
        myPie.setLabels(labels)


        #myPie.explode = [10,10,10,10,10,10,10,10,10,10]
        
        myPie.color = ["red", "green", "yellow", "orange", "blue", "red", "green", "yellow", "orange", "blue"]
        myPie.draw("%s/graphs/quota_pie.png" % settings.MEDIA_ROOT)
        


    def gen_trend_graph(self, start, end, machine_category):
        """Generates a bar graph showing the trend usage for a machine category
        
        Keyword arguments:
        start -- start date
        end -- end date
        machine_category -- MachineCategory object
        """
        
        start_str = start.strftime('%Y-%m-%d')
        end_str = end.strftime('%Y-%m-%d')
        
        period = (end - start).days
        
        x = gdchart.Bar()
        x.width = 700
        x.height = 350
        x.bg_color = "white"
        x.xtitle = "Days"
        x.ytitle = "CPU Time (hours)"
        x.title = '%s - %s-%s' % (machine_category.name, start_str, end_str)
        x.grid = "NONE"
        
        today = datetime.date.today()
        
        mc_ids = tuple([(int(m.id)) for m in machine_category.machine_set.all()])
        if len(mc_ids) == 1:
            mc_ids = "(%i)" % mc_ids[0]

        cursor = connection.cursor()
        
        SQL = "SELECT date, SUM( cpu_usage ) FROM `cpu_job` WHERE `machine_id` IN %s AND `date` >= '%s' AND `date` <= '%s' Group By date" % (mc_ids, start_str, end_str)
        cursor.execute(SQL)
        rows = dict(cursor.fetchall())
        
        data, colours = smooth_data(rows, start, end)
        
        x.ext_color = colours
        x.setData(data)
        try:
            x.draw("%s/graphs/trends/trend_%i_%s-%s.png" % (settings.MEDIA_ROOT, machine_category.id, start_str, end_str))
        except:
            pass


    def gen_institute_bar(self, institute, start, end, machine_category): 
        """Generates a bar graph showing the trend usage for an institute

        Keyword arguments:
        institute -- Institute
        start -- start date
        end -- end date
        machine_category -- MachineCategory object
        """
 
        start_str = start.strftime('%Y-%m-%d')
        end_str = end.strftime('%Y-%m-%d')
        
        period = (end - start).days
        
        x = gdchart.Bar()
        x.width = 700
        x.height = 350
        x.bg_color = "white"
        x.xtitle = "Days"
        x.ytitle = "CPU Time (hours)"
        x.title = '%s - %s-%s' % (institute.name, start_str, end_str)
        x.grid = "NONE"
        
        rows = get_insitutes_trend(institute, start, end, machine_category)
        
        data, colours = smooth_data(rows, start, end)

        x.ext_color = colours
        x.setData(data)
        #x.setComboData(data)
        try:
            x.draw("%s/graphs/institutes/bar_%s_%s-%s_%i.png" % (settings.MEDIA_ROOT, institute.id, start_str, end_str, machine_category.id))
        except:
            pass




    def gen_institutes_trend(self, start, end, machine_category):
    
        start_str = start.strftime('%Y-%m-%d')
        end_str = end.strftime('%Y-%m-%d')
        
        period = (end - start).days
        today = datetime.date.today()
        
        i_start = start
        i_end = end
        
        for i in Institute.primary.all():
            start = i_start
            end = i_end
            rows = get_insitutes_trend(i, start, end, machine_category)
            i_data, i_colours = smooth_data(rows, start, end)
            
            x = gdchart.Line()
            x.width = 700
            x.height = 350
            x.bg_color = "white"
            x.xtitle = "Days"
            x.ytitle = "CPU Time (hours)"
            x.title = '%s - %s-%s' % (i.name, start_str, end_str)
            x.grid = "NONE"

            x.setData(i_data)
            x.draw("%s/graphs/i_trends/%s_%s_%s-trend.png" % (settings.MEDIA_ROOT, i.name.replace(' ', '').lower(), start_str, end_str))
            
