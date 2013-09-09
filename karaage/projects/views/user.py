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
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from karaage.people.models import Person
from karaage.institutes.models import Institute
from karaage.projects.forms import UserProjectForm as ProjectForm
from karaage.projects.models import Project
from karaage.projects.utils import remove_user_from_project
from karaage.util import log_object as log


@login_required
def add_edit_project(request, project_id):

    project = get_object_or_404(Project, pk=project_id)
    if not request.user.get_profile() in project.leaders.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    if request.method == 'POST':

        form = ProjectForm(request.POST, instance=project)
        
        if form.is_valid():
            project = form.save()
            messages.success(request, "Project edited successfully")
            log(request.user, project, 2, "Edited project")
            return HttpResponseRedirect(project.get_absolute_url())
    else:
        form = ProjectForm(instance=project)

    return render_to_response('projects/user_project_form.html', {'form': form, 'project': project}, context_instance=RequestContext(request))


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if not project.can_view(request.user):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    return render_to_response('projects/user_project_detail.html', locals(), context_instance=RequestContext(request))


@login_required
def institute_projects_list(request, institute_id):

    institute = get_object_or_404(Institute, pk=institute_id)

    if not institute.can_view(request.user):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    project_list = institute.project_set.all()

    return render_to_response(
        'projects/institute_projects_list.html',
        {'project_list': project_list, 'institute': institute},
        context_instance=RequestContext(request))


@login_required
def remove_user(request, project_id, username):

    project = get_object_or_404(Project, pk=project_id)
    person = get_object_or_404(Person, username=username)

    if not request.user.get_profile() in project.leaders.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    if request.method == 'POST':
        remove_user_from_project(person, project)
        messages.success(request, "User '%s' removed succesfully from project %s" % (person, project.pid))
    
        log(request.user, project, 3, 'Removed %s from project' % person)
        log(request.user, person, 3, 'Removed from project %s' % project)
        return HttpResponseRedirect(project.get_absolute_url())
    
    return render_to_response('projects/remove_user_confirm.html', {'project': project, 'person': person}, context_instance=RequestContext(request))
