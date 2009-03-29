from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import permission_required, login_required
from django.core.paginator import QuerySetPaginator
from django_common.util.filterspecs import Filter, FilterBar

import datetime
from django_surveys.models import SurveyGroup

from karaage.projectreports.models import ProjectSurvey
from karaage.projects.models import Project

@login_required
def report_list(request):

    report_list = ProjectSurvey.objects.filter(date_submitted__isnull=False)

    page_no = int(request.GET.get('page', 1))

    if request.REQUEST.has_key('institute'):
        report_list = report_list.filter(survey_group=int(request.GET['survey_group']))

    filter_list = []
    filter_list.append(Filter(request, 'survey_group', SurveyGroup.objects.all()))
    filter_bar = FilterBar(request, filter_list)

    p = QuerySetPaginator(report_list, 50)
    page = p.page(page_no)

    return render_to_response('projectreports/report_list.html', locals(), context_instance=RequestContext(request))



def report_detail(request, report_id):
    
    report = get_object_or_404(ProjectSurvey, pk=report_id)


    return render_to_response('projectreports/report_detail.html', locals(), context_instance=RequestContext(request))


def still_to_complete_list(request):

    today = datetime.date.today()
    survey_group = get_object_or_404(SurveyGroup, start_date__year=today.year)
    
    survey_list = survey_group.survey_set.all()

    survey_ids = [x.projectsurvey.project.pid for x in survey_list]
    
    from karaage.projects.views.admin import project_list
    return project_list(request, Project.active.exclude(pid__in=survey_ids))
