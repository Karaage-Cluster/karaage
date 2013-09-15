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
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


from karaage.admin.models import LogEntry
from karaage.common.decorators import admin_required
from karaage.people.models import Person, Group
from karaage.projects.models import Project


@admin_required
def admin_index(request):
    newest_users = Person.objects.order_by('-date_approved', '-id').filter(date_approved__isnull=False).select_related()[:5]
    newest_projects = Project.objects.order_by('-date_approved').filter(date_approved__isnull=False).filter(is_active=True).select_related()[:5]

    recent_actions = request.user.logentry_set.all()[:10]

    return render_to_response('index.html', locals(), context_instance=RequestContext(request))


@admin_required
def search(request):

    if 'sitesearch' in request.GET and request.GET['sitesearch'].strip() != "":
        user_list = Person.objects.all()
        group_list = Group.objects.all()
        project_list = Project.objects.all()

        new_data = request.GET.copy()
        siteterms = new_data['sitesearch'].lower()
        term_list = siteterms.split(' ')

        # users
        query = Q()
        for term in term_list:
            q = Q(username__icontains=term) | Q(short_name__icontains=term) | Q(full_name__icontains=term) | Q(email__icontains=term)
            query = query & q

        user_list = user_list.filter(query).distinct()

        # groups
        query = Q()
        for term in term_list:
            q = Q(name__icontains=term) | Q(description__icontains=term)
            query = query & q

        group_list = group_list.filter(query)

         # projects
        query = Q()
        for term in term_list:
            q = Q(pid__icontains=term) | Q(name__icontains=term) | Q(leaders__username__icontains=term) | Q(leaders__short_name__icontains=term) | Q(leaders__full_name__icontains=term)
            query = query & q

        project_list = project_list.filter(query).distinct()

        empty = False

        if not (user_list or group_list or project_list):
            empty = True
        
        return render_to_response('site_search.html', locals(), context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('index'))


@admin_required
def log_list(request):
    log_list = LogEntry.objects.all()
    paginator = Paginator(log_list, 50)

    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page_obj = paginator.page(paginator.num_pages)

    return render_to_response(
                ['%s/log_list.html' % "admin", 'log_list.html'],
                {'page_obj': page_obj, 'short': True},
                context_instance=RequestContext(request))


@admin_required
def log_detail(request, object_id, model):
    obj = get_object_or_404(model, pk=object_id)
    content_type = ContentType.objects.get_for_model(model)

    log_list = LogEntry.objects.filter(
        content_type=content_type,
        object_id=object_id
    )
    paginator = Paginator(log_list, 50)

    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page_obj = paginator.page(paginator.num_pages)

    return render_to_response(['%s/log_list.html' % "admin", 'log_list.html'],
                {'page_obj': page_obj, 'short': True},
                context_instance=RequestContext(request))


@admin_required
def misc(request):
    from karaage.legacy.simple import direct_to_template
    return direct_to_template(request,
            template='misc/index.html')
