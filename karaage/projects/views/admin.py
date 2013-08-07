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
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib import messages

from andsome.util.filterspecs import Filter, FilterBar

from karaage.people.models import Person
from karaage.institutes.models import Institute
from karaage.machines.models import MachineCategory, Account
from karaage.projects.models import Project
from karaage.projects.forms import ProjectForm
from karaage.projects.utils import get_new_pid, add_user_to_project, remove_user_from_project
from karaage.util import log_object as log
from karaage.usage.forms import UsageSearchForm


@permission_required('projects.add_project')
def add_edit_project(request, project_id=None):

    if project_id is None:
        project = None
        flag = 1
    else:
        project = get_object_or_404(Project, pk=project_id)
        flag = 2

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        
        if form.is_valid():
            project = form.save(commit=False)
            if project_id is not None:
                # if project is being edited, project_id cannot change, so we
                # should always use the value supplied on the URL.
                project.pid = project_id
            elif not project.pid:
                # if project was being created, did the user give a project_id
                # we should use? If not, then we have to generate one
                # ourselves.
                project.pid = get_new_pid(project.institute)
            project.save()
            project.activate()
            form.save_m2m()
            if flag == 1:
                messages.success(request, "Project '%s' created succesfully" % project)
                log(None, project, 1, 'Created')
            else:
                messages.success(request, "Project '%s' edited succesfully" % project)
                log(None, project, 2, 'Edited')

            return HttpResponseRedirect(project.get_absolute_url())
    else:
        form = ProjectForm(instance=project)

    return render_to_response('projects/project_form.html', locals(), context_instance=RequestContext(request))


@permission_required('projects.delete_project')
def delete_project(request, project_id):

    project = get_object_or_404(Project, pk=project_id)

    query = Account.objects.filter(date_deleted__isnull=True, default_project=project)

    error = None
    if query.count() > 0:
        error = "There are accounts that use this project as the default_project."

    elif request.method == 'POST':
        project.deactivate()
        log(request.user, project, 3, 'Deleted')
        messages.success(request, "Project '%s' deleted succesfully" % project)
        return HttpResponseRedirect(project.get_absolute_url())

    del query

    return render_to_response('projects/project_confirm_delete.html',
            { 'project': project, 'error': error },
            context_instance=RequestContext(request))

    
@login_required
def project_detail(request, project_id):

    project = get_object_or_404(Project, pk=project_id)
    user_list = Person.active.select_related()

    form = UsageSearchForm()
    
    if request.method == 'POST':
        # Post means adding a user to this project
        if not request.user.has_perm('projects.change_project'):
            return HttpResponseForbidden('<h1>Access Denied</h1>')
        
        data = request.POST.copy()
        if data['person']:
            person = Person.objects.get(pk=data['person'])
            add_user_to_project(person, project)
        return HttpResponseRedirect(project.get_absolute_url())

    return render_to_response('projects/project_detail.html',
                              {'project': project, 'user_list': user_list, 'form': form},
                              context_instance=RequestContext(request))


@login_required
def project_list(request, queryset=Project.objects.select_related(), template_name='projects/project_list.html', paginate=True):

    project_list = queryset

    # Make sure page request is an int. If not, deliver first page.
    try:
        page_no = int(request.GET.get('page', '1'))
    except ValueError:
        page_no = 1

    if 'institute' in request.REQUEST:
        project_list = project_list.filter(institute=int(request.GET['institute']))

    if 'status' in request.REQUEST:
        project_list = project_list.filter(is_active=int(request.GET['status']))

    if 'search' in request.REQUEST:
        terms = request.REQUEST['search'].lower()
        query = Q()
        for term in terms.split(' '):
            q = Q(pid__icontains=term) | Q(name__icontains=term) | Q(description__icontains=term) | Q(leaders__user__first_name__icontains=term) | Q(leaders__user__last_name__icontains=term) | Q(institute__name__icontains=term)
            query = query & q
        
        project_list = project_list.filter(query)
    else:
        terms = ""

    filter_list = []
    filter_list.append(Filter(request, 'status', {1: 'Active', 0: 'Deleted'}))
    filter_list.append(Filter(request, 'institute', Institute.active.all()))
    filter_bar = FilterBar(request, filter_list)

    if paginate:
        p = Paginator(project_list, 50)
    else:
        p = Paginator(project_list, 100000)

    # If page request (9999) is out of range, deliver last page of results.
    try:
        page = p.page(page_no)
    except (EmptyPage, InvalidPage):
        page = p.page(p.num_pages)

    return render_to_response(
            template_name,
            {'page': page, 'filter_bar': filter_bar, 'project_list': project_list, 'terms': terms},
            context_instance=RequestContext(request))


@permission_required('projects.change_project')
def remove_user(request, project_id, username):

    project = get_object_or_404(Project, pk=project_id)
    person = get_object_or_404(Person, user__username=username)

    query = person.account_set.filter(date_deleted__isnull=True, default_project=project)

    error = None
    if query.count() > 0:
        error = "The person has accounts that use this project as the default_project."

    elif request.method == 'POST':
        remove_user_from_project(person, project)
        messages.success(request, "User '%s' removed succesfully from project %s" % (person, project.pid))

        log(request.user, project, 3, 'Removed %s from project' % person)
        log(request.user, person, 3, 'Removed from project %s' % project)

        return HttpResponseRedirect(project.get_absolute_url())

    del query

    return render_to_response('projects/remove_user_confirm.html',
        { 'project': project, 'person': person, 'error': error, },
        context_instance=RequestContext(request))


@login_required
def no_users(request):

    project_ids = []
    for p in Project.active.all():
        if p.group.members.count() == 0:
            project_ids.append(p.pid)

    return project_list(request, Project.objects.filter(pid__in=project_ids))


@login_required
def over_quota(request):

    project_ids = []

    for p in Project.active.all():
        for pc in p.projectchunk_set.all():
            if pc.is_over_quota():
                project_ids.append(p.pid)

    return project_list(request, Project.objects.filter(pid__in=project_ids))


@login_required
def project_logs(request, project_id):

    project = get_object_or_404(Project, pk=project_id)

    log_list = LogEntry.objects.filter(
        content_type=ContentType.objects.get_for_model(project.__class__),
        object_id=project_id
    )

    short = True
    return render_to_response('log_list.html',
                              {'log_list': log_list, 'short': short, 'project': project},
                              context_instance=RequestContext(request))
