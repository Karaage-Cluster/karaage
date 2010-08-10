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

    if not person in project.leaders.all():
        if not request.user.has_perm('projectreports.add_projectsurvey'):
            return HttpResponseForbidden("Access Denied - must be project leader.")
    
    today = datetime.date.today()
    
    survey_group = get_object_or_404(SurveyGroup, start_date__year=today.year)
    survey, created = ProjectSurvey.objects.get_or_create(project=project, survey_group=survey_group)
    survey.submitter = project.pid
    survey.save()

    return do_survey(request, survey, template_name='surveys/projectsurvey%s.html' % today.year, extra_context={'project': project }, redirect_url='thanks/')


@login_required
def thanks(request, project_id):
    
    person = request.user.get_profile()
    
    project = get_object_or_404(Project, pk=project_id)

    if not person in project.leaders.all():
        if not request.user.has_perm('projectreports.add_projectsurvey'):
            return HttpResponseForbidden("Access Denied - must be project leader.")
    
    today = datetime.date.today()
    survey_group = get_object_or_404(SurveyGroup, start_date__year=today.year)

    survey, created = ProjectSurvey.objects.get_or_create(project=project, survey_group=survey_group)

    if created:
        return HttpResponseRedirect(reverse('kg_survey', args=project.pid))


    return render_to_response('surveys/thanks.html', locals(), context_instance=RequestContext(request))
