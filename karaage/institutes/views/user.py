from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from karaage.people.models import Institute



@login_required
def institute_users_list(request, institute_id):

    institute = get_object_or_404(Institute, pk=institute_id)

    ids = [ institute.delegate.id , institute.active_delegate.id, ]

    if not request.user.get_profile().id in ids:
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    user_list = institute.person_set.all()

    return render_to_response('institutes/institute_user_list.html', locals(), context_instance=RequestContext(request))


@login_required
def institute_projects_list(request, institute_id):

    institute = get_object_or_404(Institute, pk=institute_id)

    ids = [ institute.delegate.id , institute.active_delegate.id, ]

    if not request.user.get_profile().id in ids:
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    project_list = institute.project_set.all()

    return render_to_response('institutes/institute_projects_list.html', locals(), context_instance=RequestContext(request))

