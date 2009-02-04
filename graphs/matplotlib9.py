"""
Graph generation using matplotlib
"""

from django.conf import settings
from django.db import connection
from django.template.defaultfilters import dictsortreversed

import matplotlib
matplotlib.use('Agg')  # force the antigrain backend
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import matplotlib.dates as dates
from pylab import arange
from decimal import Decimal
import datetime

from karaage.people.models import Institute
from karaage.projects.models import Project
from karaage.machines.models import MachineCategory, UserAccount
from karaage.usage.models import CPUJob
from karaage.util.helpers import get_available_time

#import gdchart2
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
        today = datetime.date.today()
        start_str = start.strftime('%Y-%m-%d')
        end_str = end.strftime('%Y-%m-%d')
        start_t = start.strftime('%d/%m/%y')
        end_t = end.strftime('%d/%m/%y')
        fig = Figure(figsize=(6,3))
        ax = fig.add_axes([0.2, 0.2, 0.7, 0.7])
        period = (end-start).days
        x_data = []
        j = 1
        while j <= period:
            x_data.append(j)
            j += 1

        ax.set_xlim(0,period+1)
        if period < 10:
            step = 1
        elif period < 100:
            step = 20
        else:
            step = 50
        ax.set_xticks(arange(period+1, step=step))
        #print drange(start, end, datetime.timedelta(days=2))


        ax.set_title('%s   %s - %s' % (project.pid, start_t, end_t))
        ax.set_ylabel("CPU Time (hours)")
        ax.set_xlabel("Days")

        mc_ids = tuple([(int(m.id)) for m in machine_category.machine_set.all()])
        if len(mc_ids) == 1:
            mc_ids = "(%i)" % mc_ids[0]
            
        t_start = start
        t_end = end
        b_total = 0
        
        user_data = []
        
        cursor = connection.cursor()
        SQL = "SELECT user_id from cpu_job where project_id = '%s' and `machine_id` IN %s AND `date` >= '%s' AND `date` <= '%s' GROUP BY user_id" % (str(project.pid), mc_ids, start_str, end_str)
        cursor.execute(SQL)
        rows = list(cursor.fetchall())
        cursor.close()

        for uid in rows:
            ua = UserAccount.objects.get(id=uid[0])
            u = ua.user



        #for u in project.users.all():

#            ua = u.get_user_account(machine_category)
#            if ua is None:
#                continue
            cursor = connection.cursor()
            SQL = "SELECT date, SUM( cpu_usage ) FROM `cpu_job` WHERE `project_id` LIKE '%s' AND `user_id` = %s AND `machine_id` IN %s AND `date` >= '%s' AND `date` <= '%s' Group By date" % (str(project.pid), str(ua.id), mc_ids, start_str, end_str)
            cursor.execute(SQL)
            rows = dict(cursor.fetchall())

        
            if rows:
                
                data, dates_y, labels  = [], [], []
                start = t_start
                end = t_end

                while start <= end:
                    if start != today:
                        try:
                            total = float(rows[start])
                        except:
                            total = 0
                        
                        data.append(total / 3600.00)
                        labels.append(str(start))
                        b_total += total
            
                    start = start + datetime.timedelta(days=1)

                user_data.append({'user': u, 'data': data, 'total': sum(data)})
                #print ua.user
                #print data
                #print '-----'
                #print 'prev: %s ' % prev_data
                #ax.bar(dates, data, color=colours[count], edgecolor=colours[count])
                #prev_data = data
            
        #print b_total/ 3600
        count = 0
        prev_data = None


        # majloc = dates.AutoDateLocator()
        # majfmt = dates.AutoDateFormatter(majloc)
    
        # ax.xaxis.set_major_locator(majloc)
        # ax.xaxis.set_major_formatter(majfmt)

        user_data = dictsortreversed(user_data, 'total')
        user_data = [d['data'] for d in user_data]
        for data in user_data:
            if prev_data:
                ax.bar(x_data, data, color=get_colour(count), edgecolor=get_colour(count), bottom=prev_data, align='center')
                p = 0
                while p < len(prev_data):
                    prev_data[p] += data[p]
                    p += 1
            else:
                ax.bar(x_data, data, color=get_colour(count), edgecolor=get_colour(count), align='center')
                prev_data = data

        
            count += 1
    
        canvas = FigureCanvasAgg(fig)
        canvas.print_figure("%s/graphs/projects/%s_%s-%s_%i.png" % (str(settings.MEDIA_ROOT), str(project.pid), str(start_str), str(end_str), machine_category.id))


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
        
        fig = Figure(figsize=(4,4))
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        ax.set_title = "Institutes Usage - (%s - %s) - %s" % (start_str, end_str, machine_category.name) 
        
        data, labels, colours = [], [], []
        total = 0
        for i in institute_list:  
            usage = i.get_usage(start, end, machine_category)
            if usage[0] is not None:
                total = total + Decimal(usage[0])
                data.append(Decimal(usage[0]))
                labels.append(i.name)
                colours.append(get_inst_colour(i.name))

        data.append(Decimal(available_time - total))
        labels.append('Unused')
        colours.append(get_inst_colour('Unused'))

        fracs = []

        for i in data:
            if total:
                fracs.append((i/total) * 100)
    
            
        ax.pie(fracs, labels=labels, colors=colours)

    
        canvas = FigureCanvasAgg(fig)
        canvas.print_figure("%s/graphs/institutes/%s-%s_%i.png" % (settings.MEDIA_ROOT, start_str, end_str, machine_category.id))



    def gen_quota_graph(self):
        """Generates a pie graph for all primary institutes quota       
        """
        institute_list = Institute.primary.exclude(name='Unknown').exclude(name='Brecca-Monash')
        fig = Figure(figsize=(6,6))
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        ax.set_title = "Institutes Quota"

    
        data, labels, colours = [], [], []
        
        for i in institute_list:  
            data.append(Decimal(i.quota))
            labels.append(i.name)
            colours.append(get_inst_colour(i.name))
            
        ax.pie(data, labels=labels, colors=colours)
            
        canvas = FigureCanvasAgg(fig)
        canvas.print_figure("%s/graphs/quota_pie.png" % settings.MEDIA_ROOT)






