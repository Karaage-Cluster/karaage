# Copyright 2007-2014 VPAC
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

import django_tables2 as tables

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


from karaage.common import is_admin
from karaage.common.decorators import admin_required
from karaage.common.models import LogEntry
from karaage.common.tables import LogEntryFilter, LogEntryTable
from karaage.people.models import Person, Group
from karaage.projects.models import Project


@admin_required
def admin_index(request):
    newest_users = Person.objects.order_by('-date_approved', '-id')
    newest_users = newest_users.filter(date_approved__isnull=False)
    newest_users = newest_users.select_related()[:5]

    newest_projects = Project.objects.order_by('-date_approved')
    newest_projects = newest_projects.filter(date_approved__isnull=False)
    newest_projects = newest_projects.filter(is_active=True)
    newest_projects = newest_projects.select_related()[:5]

    recent_actions = request.user.logentry_set.all()[:10]

    var = {
        'newest_users': newest_users,
        'newest_projects': newest_projects,
        'recent_actions': recent_actions,
    }
    return render_to_response(
        'common/index.html', var, context_instance=RequestContext(request))


def index(request):
    if settings.ADMIN_REQUIRED or is_admin(request):
        return admin_index(request)
    return render_to_response(
        'common/index.html', context_instance=RequestContext(request))


@admin_required
def search(request):

    if 'sitesearch' in request.GET and request.GET['sitesearch'].strip() != "":
        people_list = Person.objects.all()
        group_list = Group.objects.all()
        project_list = Project.objects.all()

        new_data = request.GET.copy()
        siteterms = new_data['sitesearch'].lower()
        term_list = siteterms.split(' ')

        # users
        query = Q()
        for term in term_list:
            q = Q(username__icontains=term)
            q = q | Q(short_name__icontains=term)
            q = q | Q(full_name__icontains=term)
            q = q | Q(email__icontains=term)
            query = query & q

        people_list = people_list.filter(query).distinct()

        # groups
        query = Q()
        for term in term_list:
            q = Q(name__icontains=term) | Q(description__icontains=term)
            query = query & q

        group_list = group_list.filter(query)

         # projects
        query = Q()
        for term in term_list:
            q = Q(pid__icontains=term)
            q = q | Q(name__icontains=term)
            q = q | Q(leaders__username__icontains=term)
            q = q | Q(leaders__short_name__icontains=term)
            q = q | Q(leaders__full_name__icontains=term)
            query = query & q

        project_list = project_list.filter(query).distinct()

        empty = False

        if not (people_list or group_list or project_list):
            empty = True

        return render_to_response(
            'common/site_search.html',
            locals(),
            context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('index'))


@admin_required
def log_list(request):
    queryset = LogEntry.objects.all()

    filter = LogEntryFilter(request.GET, queryset=queryset)
    table = LogEntryTable(filter)
    tables.RequestConfig(request).configure(table)

    spec = []
    for name, value in filter.form.cleaned_data.iteritems():
        if value is not None and value != "":
            name = name.replace('_', ' ').capitalize()
            spec.append((name, value))

    return render_to_response(
        'common/log_list.html',
        {
            'table': table,
            'filter': filter,
            'spec': spec,
            'title': "Institute list",
        },
        context_instance=RequestContext(request))


@admin_required
def misc(request):
    from karaage.common.simple import direct_to_template
    return direct_to_template(
        request,
        template='common/misc_detail.html')


def aup(request):
    from karaage.common.simple import direct_to_template
    return direct_to_template(
        request,
        template='common/aup_detail.html')
