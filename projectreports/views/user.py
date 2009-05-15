from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.contrib.auth.decorators import login_required

import datetime
from django_surveys.models import SurveyGroup
from django_surveys.views import do_survey

from karaage.projects.models import Project
from karaage.people.models import Person
from karaage.projectreports.models import ProjectSurvey

@login_required
def survey(request, project_id):
    
    person = request.user.get_profile()
    
    project = get_object_or_404(Project, pk=project_id)

    if not person == project.leader:
        if not request.user.has_perm('projectreports.add_projectsurvey'):
            return HttpResponseForbidden("Access Denied - must be project leader.")
    
    today = datetime.date.today()
    
    survey_group = get_object_or_404(SurveyGroup, start_date__year=today.year)
    survey, created = ProjectSurvey.objects.get_or_create(project=project, survey_group=survey_group)
    survey.submitter = project.pid
    survey.save()

    return do_survey(request, survey.id, template_name='surveys/projectsurvey%s.html' % today.year, extra_context={'project': project })


@login_required
def thanks(request, project_id):
    
    person = request.user.get_profile()
    
    project = get_object_or_404(Project, pk=project_id)

    if not person == project.leader:
        if not request.user.has_perm('projectreports.add_projectsurvey'):
            return HttpResponseForbidden("Access Denied - must be project leader.")
    
    today = datetime.date.today()
    survey_group = get_object_or_404(SurveyGroup, start_date__year=today.year)

    survey, created = ProjectSurvey.objects.get_or_create(project=project, survey_group=survey_group)

    if created:
        return HttpResponseRedirect(reverse('kg_survey'))


    return render_to_response('surveys/thanks.html', locals(), context_instance=RequestContext(request))
