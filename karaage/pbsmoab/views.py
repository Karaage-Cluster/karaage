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
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required

from karaage.projects.models import Project
from karaage.util import log_object as log

from models import ProjectChunk
from forms import ProjectChunkForm

@permission_required('pbsmoab.change_projectchunk')
def projectchunk_edit(request, project_id):

    project = get_object_or_404(Project, pk=project_id)
    
    project_chunk, created = ProjectChunk.objects.get_or_create(project=project)
    old_cap = project_chunk.cap

    if request.method == 'POST':
        form = ProjectChunkForm(request.POST, instance=project_chunk)
        if form.is_valid():
            project_chunk = form.save()
            new_cap = project_chunk.cap
            if old_cap != new_cap:
                log(request.user, project, 2, 'Changed cap from %s to %s' % (old_cap, new_cap))
            return HttpResponseRedirect(project.get_absolute_url())

    else:
        form = ProjectChunkForm(instance=project_chunk)

    return render_to_response('pbsmoab/projectchunk_form.html', locals(), context_instance=RequestContext(request))


def projects_by_cap_used(request):
    from karaage.projects.views.admin import project_list
    return project_list(request, queryset=Project.active.all(), paginate=False, template_name='pbsmoab/project_capsort.html')
    
    
