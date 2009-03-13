from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.paginator import QuerySetPaginator
from django.conf import settings

from django_common.util.filterspecs import Filter, FilterBar

from karaage.util.graphs import get_institute_trend_graph_url
from karaage.people.models import Institute


def institute_detail(request, institute_id):
    
    institute = get_object_or_404(Institute, pk=institute_id)

    if institute.is_primary():
        graph = get_institute_trend_graph_url(institute)
    
    return render_to_response('institutes/institute_detail.html', locals(), context_instance=RequestContext(request))
    

def institute_list(request):

    institute_list = Institute.objects.all()
    page_no = int(request.GET.get('page', 1))

    if request.REQUEST.has_key('primary'):
        institute_list = Institute.primary.all()


    filter_list = []
    filter_list.append(Filter(request, 'primary', {'primary': 'Primary',}))
    filter_bar = FilterBar(request, filter_list)

    p = QuerySetPaginator(institute_list, 50)
    page = p.page(page_no)

    return render_to_response('institutes/institute_list.html', locals(), context_instance=RequestContext(request))

