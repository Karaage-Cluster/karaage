from django.template import Library

from django_common.graphs.googlechart import GraphGenerator

grapher = GraphGenerator()
register = Library()

@register.simple_tag
def mc_pie_chart(machine_category, start, end):

    data = {}
    for m in machine_category.machine_set.all():  
        usage = m.get_usage(start, end)
        if usage[0] is not None:
            data[m.name] = float(usage[0])
            
    return grapher.pie_chart(data_dict=data).get_url()

