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
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

import datetime

from karaage.people.models import Institute
from karaage.projects.forms import UserProjectForm as ProjectForm
from karaage.projects.models import Project
from karaage.machines.models import Machine
from karaage.util.email_messages import *

@login_required
def add_edit_project(request, project_id=None):

    if project_id is None:
        project = False
    else :
        project = get_object_or_404(Project, pk=project_id)
        if not request.user == project.leader.user:
            return HttpResponseForbidden('<h1>Access Denied</h1>')
                                    
    leader = request.user.get_profile()
    
    if request.method == 'POST':

        form = ProjectForm(request.POST)
        
        if form.is_valid():
            if project:
                # edit
                form.save(p=project)
                request.user.message_set.create(message="Project edited successfully")
                return HttpResponseRedirect(reverse('kg_user_profile'))
            else:
                # add
                project_request = form.save(leader=leader)
                # Send email to Institute Delegate for approval
                send_project_request_email(project_request)
                                                
                return HttpResponseRedirect(reverse('project_created', args=[project_request.id]))                            	    
    else:        
        form = ProjectForm()
        form.initial['institute'] = request.user.get_profile().institute.id
        if project:

            form.initial = project.__dict__
            form.initial['machine_category'] = form.initial['machine_category_id']
            form.initial['leader'] = form.initial['leader_id']
            form.initial['institute'] = form.initial['institute_id']
    return render_to_response('projects/user_project_form.html', { 'form': form, 'project': project }, context_instance=RequestContext(request))



def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    return render_to_response('projects/user_project_detail.html', locals(), context_instance=RequestContext(request))


@login_required
def institute_projects_list(request, institute_id):

    institute = get_object_or_404(Institute, pk=institute_id)

    ids = [ institute.delegate.id , institute.active_delegate.id, ]

    if not request.user.get_profile().id in ids:
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    project_list = institute.project_set.all()

    return render_to_response('projects/institute_projects_list.html', locals(), context_instance=RequestContext(request))

