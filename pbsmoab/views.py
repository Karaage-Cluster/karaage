from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required

from karaage.projects.models import Project
from karaage.util import log_object as log

from models import ProjectChunk
from forms import ProjectChunkForm

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

projectchunk_edit = permission_required('pbsmoab.change_projectchunk')(projectchunk_edit)
    
