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
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from karaage.people.models import Person
from karaage.projects.models import Project
from karaage.requests.models import ProjectJoinRequest, ProjectCreateRequest


@login_required
def admin_index(request):
    newest_users = Person.objects.order_by('-date_approved', '-id').filter(date_approved__isnull=False)[:5]
    newest_projects = Project.objects.order_by('-date_approved').filter(date_approved__isnull=False).filter(is_active=True)[:5]
    
    userrequest_list = ProjectJoinRequest.objects.filter(leader_approved=False)
    projectrequest_list = ProjectCreateRequest.objects.all()

    recent_actions = request.user.logentry_set.all()[:10]

    return render_to_response('index.html', locals(), context_instance=RequestContext(request))


@login_required
def search(request):

    if request.method == 'POST':

        user_list = Person.objects.all()
        project_list = Project.objects.all()

        new_data = request.POST.copy()
        siteterms = new_data['sitesearch'].lower()
        term_list = siteterms.split(' ')

        if term_list[0] == "":
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

        
        # users
        query = Q()
        for term in term_list:
            q = Q(user__username__icontains=term) | Q(user__first_name__icontains=term) | Q(user__last_name__icontains=term) | Q(user__email__icontains=term)  
            query = query & q

        user_list = user_list.filter(query)

         # projects
        query = Q()
        for term in term_list:
            q = Q(pid__icontains=term) | Q(name__icontains=term) | Q(leaders__user__username__icontains=term) | Q(leaders__user__first_name__icontains=term) | Q(leaders__user__last_name__icontains=term) 
            query = query & q

        project_list = project_list.filter(query)

        empty = False

        if not (user_list or project_list):
            empty = True
        
        return render_to_response('site_search.html', locals(), context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('kg_admin_index'))


def log_detail(request, object_id, model):

    obj = get_object_or_404(model, pk=object_id)
    content_type = ContentType.objects.get_for_model(model)

    log_list = LogEntry.objects.filter(
        content_type=content_type,
        object_id=object_id
    )
    page_no = 1
    p = Paginator(log_list, 50)
    page_obj = p.page(page_no)
    
    short = True
    return render_to_response(['%s/log_list.html' % content_type.app_label, 'log_list.html'], locals(), context_instance=RequestContext(request))


@login_required
def comments_detail(request, object_id, model):
    obj = get_object_or_404(model, pk=object_id)
    content_type = ContentType.objects.get_for_model(obj.__class__)
    return render_to_response('comments/%s_detail.html' % content_type.model, locals(), context_instance=RequestContext(request))


@login_required
def add_comment(request, object_id, model):

    obj = get_object_or_404(model, pk=object_id)

    if request.method == 'POST':

        content_type = ContentType.objects.get_for_model(obj.__class__)
        comment = request.POST['comment']
        
        Comment.objects.create(
            user=request.user,
            content_type=content_type,
            comment=comment,
            object_id=object_id,
            site=Site.objects.get_current(),
            valid_rating=0,
            is_public=True,
            is_removed=False)

        return HttpResponseRedirect(obj.get_absolute_url())
    else:
        field = forms.CharField(widget=forms.Textarea(), label='Comment').widget.render('comment', '')

    return render_to_response('comments/add_comment.html', locals(), context_instance=RequestContext(request))
    

@login_required
def meta(request):
    
    meta_data = request.META.items()

    return render_to_response('meta.html', {'meta': metadata}, context_instance=RequestContext(request))
