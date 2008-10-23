from django.conf import settings
import datetime
from karaage.machines.models import MachineCategory
from karaage.people.models import Institute
from karaage.graphs import *

def get_institute_graph_url(start, end, machine_category):

    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    if settings.GRAPH_DEBUG:
        gen_institutes_pie(start, end, machine_category)

    try:
        f = open("%s/graphs/institutes/%s-%s_%i.png" % (settings.MEDIA_ROOT, start_str, end_str, machine_category.id))
    except:
        try:
            gen_institutes_pie(start, end, machine_category)
        except:
            return ''
        
    return "institutes/%s-%s_%i.png" % (start_str, end_str, machine_category.id)

    
def get_trend_graph_url(start, end, machine_category):

    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')
    
    if settings.GRAPH_DEBUG:
        gen_trend_graph(start, end, machine_category)

    try:
        f = open("%s/graphs/trends/trend_%i_%s-%s.png" % (settings.MEDIA_ROOT, machine_category.id, start_str, end_str))
    except:
        try:
            gen_trend_graph(start, end, machine_category)
        except:
            return ''

    return "trends/trend_%i_%s-%s.png" % (machine_category.id, start_str, end_str)



def get_institute_trend_graph_url(institute, 
                                  start=datetime.date.today()-datetime.timedelta(days=90), 
                                  end=datetime.date.today(), 
                                  machine_category=MachineCategory.objects.get_default()):


    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    if settings.GRAPH_DEBUG:
        institute.gen_usage_graph(start, end, machine_category)

    try:
        f = open("%s/graphs/institutes/bar_%i_%s-%s_%i.png" % (settings.MEDIA_ROOT, institute.id, start_str, end_str, machine_category.id))
    except:
        try:
            institute.gen_usage_graph(start, end, machine_category)
        except:
            return ''
            
    return "bar_%i_%s-%s_%i.png" % (institute.id, start_str, end_str, machine_category.id)


def get_project_trend_graph_url(project, 
                                start=datetime.date.today()-datetime.timedelta(days=90), 
                                end=datetime.date.today(), 
                                machine_category=MachineCategory.objects.get_default()):

    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    if settings.GRAPH_DEBUG:
        gen_project_graph(project, start, end, machine_category)

    try:
        f = open("%s/graphs/projects/%s_%s-%s_%i.png" % (settings.MEDIA_ROOT, project.pid, start_str, end_str, machine_category.id))
    except:
        try:
            gen_project_graph(project, start, end, machine_category)
        except:
            return ''

    return "%s_%s-%s_%i.png" % (project.pid, start_str, end_str, machine_category.id)


def get_institutes_trend_graph_urls(start, end, machine_category=MachineCategory.objects.get_default()):

    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    if settings.GRAPH_DEBUG:
        gen_institutes_trend(start, end, machine_category)

    try:
        for i in Institute.primary.all():
            f = open("%s/graphs/i_trends/%s_%s_%s-trend.png" % (settings.MEDIA_ROOT, i.name.replace(' ', '').lower(), start_str, end_str)) 
    except:
        try:
            gen_institutes_trend(start, end, machine_category)
        except:
            return ''

    graph_list = []
    for i in Institute.primary.all():
        graph_list.append("%s_%s_%s-trend.png" % (i.name.replace(' ', '').lower(), start_str, end_str))

    
    return graph_list
