from django.conf import settings
from accounts.main.models import MachineCategory

module = __import__(settings.GRAPH_LIB, {}, {}, [''])

grapher = module.GraphGenerator()


def gen_project_graph(project, start, end, machine_category=MachineCategory.objects.get_default()):
    return grapher.gen_project_graph(project, start, end, machine_category)

def gen_institutes_pie(start, end, machine_category=MachineCategory.objects.get_default()):
      return grapher.gen_institutes_pie(start, end, machine_category)  

def gen_quota_graph():
    return grapher.gen_quota_graph()

def gen_trend_graph(start, end, machine_category=MachineCategory.objects.get_default()):
    return grapher.gen_trend_graph(start, end, machine_category)

def gen_institute_bar(institute, start, end, machine_category=MachineCategory.objects.get_default()): 
    return grapher.gen_institute_bar(institute, start, end, machine_category)

def gen_institutes_trend(start, end, machine_category=MachineCategory.objects.get_default()): 
    return grapher.gen_institutes_trend(start, end, machine_category)
