# Copyright 2007-2013 VPAC
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
from django.http import HttpResponseRedirect
from django.forms import util

from karaage.util.decorators import admin_required
from karaage.projects.models import Project
from karaage.util import log_object as log
from karaage.pbsmoab.models import ProjectChunk
from karaage.pbsmoab.forms import ProjectChunkForm


@admin_required
def projectchunk_add(request, project_id):

    project = get_object_or_404(Project, pk=project_id)
    
    project_chunk = ProjectChunk()
    project_chunk.project = project

    if request.method == 'POST':
        form = ProjectChunkForm(request.POST, instance=project_chunk)
        if form.is_valid():
            mc = form.cleaned_data['machine_category']
            conflicting = ProjectChunk.objects.filter(
                project=project,machine_category=mc)

            if conflicting.count() >= 1:
                form._errors["machine_category"] = util.ErrorList(["Cap already exists with this machine category"])
            else:
                project_chunk = form.save()
                new_cap = project_chunk.cap
                log(request.user, project, 2, 'Added cap of %s' % (new_cap))
                return HttpResponseRedirect(project.get_absolute_url())
    else:
        form = ProjectChunkForm(instance=project_chunk)

    return render_to_response('pbsmoab/projectchunk_form.html', locals(), context_instance=RequestContext(request))


@admin_required
def projectchunk_edit(request, projectchunk_id):

    project_chunk = get_object_or_404(ProjectChunk, pk=projectchunk_id)
    old_cap = project_chunk.cap
    old_mc = project_chunk.machine_category

    if request.method == 'POST':
        form = ProjectChunkForm(request.POST, instance=project_chunk)
        if form.is_valid():
            mc = form.cleaned_data['machine_category']
            if old_mc.pk != mc.pk:
                form._errors["machine_category"] = util.ErrorList(["Please don't change the machine category; it confuses me"])
            else:
                project_chunk = form.save()
                new_cap = project_chunk.cap
                if old_cap != new_cap:
                    log(request.user, project_chunk.project, 2, 'Changed cap from %s to %s' % (old_cap, new_cap))
                return HttpResponseRedirect(project_chunk.project.get_absolute_url())

    else:
        form = ProjectChunkForm(instance=project_chunk)

    return render_to_response('pbsmoab/projectchunk_form.html', locals(), context_instance=RequestContext(request))


@admin_required
def projectchunk_delete(request, projectchunk_id):

    project_chunk = get_object_or_404(ProjectChunk, pk=projectchunk_id)

    if request.method == 'POST':
	project_chunk.delete()
        return HttpResponseRedirect(project_chunk.project.get_absolute_url())

    return render_to_response('pbsmoab/projectchunk_delete_form.html', locals(), context_instance=RequestContext(request))


@admin_required
def projects_by_cap_used(request):
    from karaage.projects.views.admin import project_list
    return project_list(request, queryset=Project.active.all(), paginate=False, template_name='pbsmoab/project_capsort.html')
    
    
