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
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib import messages
from django.core.urlresolvers import reverse

from andsome.util.filterspecs import Filter, FilterBar

from karaage.common.decorators import admin_required
from karaage.people.models import Person
from karaage.institutes.models import Institute
from karaage.machines.models import MachineCategory, Account
from karaage.projects.models import Project, ProjectQuota
from karaage.projects.forms import ProjectForm, ProjectQuotaForm, AddPersonForm
from karaage.projects.utils import get_new_pid, add_user_to_project, remove_user_from_project
from karaage.common import log_object as log
import karaage.common as util


@admin_required
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
            approved_by = request.user
            project.activate(approved_by)
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


@admin_required
def delete_project(request, project_id):

    project = get_object_or_404(Project, pk=project_id)

    query = Account.objects.filter(date_deleted__isnull=True, default_project=project)

    error = None
    if query.count() > 0:
        error = "There are accounts that use this project as the default_project."

    elif request.method == 'POST':
        deleted_by = request.user
        project.deactivate(deleted_by)
        log(request.user, project, 3, 'Deleted')
        messages.success(request, "Project '%s' deleted succesfully" % project)
        return HttpResponseRedirect(project.get_absolute_url())

    del query

    return render_to_response('projects/project_confirm_delete.html',
            { 'project': project, 'error': error },
            context_instance=RequestContext(request))

    
@admin_required
def project_detail(request, project_id):

    project = get_object_or_404(Project, pk=project_id)

    form = AddPersonForm(request.POST or None)
    if request.method == 'POST':
        # Post means adding a user to this project
        if form.is_valid():
            person = form.cleaned_data['person']
            add_user_to_project(person, project)
            messages.success(request, "User '%s' was added to %s succesfully" % (person, project))
            return HttpResponseRedirect(project.get_absolute_url())

    return render_to_response('projects/project_detail.html',
                              {'project': project, 'form': form},
                              context_instance=RequestContext(request))


@admin_required
def project_verbose(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    from karaage.datastores import get_project_details
    project_details = get_project_details(project)

    return render_to_response('projects/project_verbose.html', locals(), context_instance=RequestContext(request))


@admin_required
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
            q = Q(pid__icontains=term) | Q(name__icontains=term) | Q(description__icontains=term) | Q(leaders__short_name__icontains=term) | Q(leaders__full_name__icontains=term) | Q(institute__name__icontains=term)
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


@admin_required
def remove_user(request, project_id, username):

    project = get_object_or_404(Project, pk=project_id)
    person = get_object_or_404(Person, username=username)

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


@admin_required
def no_users(request):

    project_ids = []
    for p in Project.active.all():
        if p.group.members.count() == 0:
            project_ids.append(p.pid)

    return project_list(request, Project.objects.filter(pid__in=project_ids))


@admin_required
def over_quota(request):

    project_ids = []

    for p in Project.active.all():
        for pc in p.projectquota_set.all():
            if pc.is_over_quota():
                project_ids.append(p.pid)

    return project_list(request, Project.objects.filter(pid__in=project_ids))


@admin_required
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

@admin_required
def add_comment(request, project_id):
    obj = get_object_or_404(Project, pk=project_id)
    return util.add_comment(request, "Projects", reverse("kg_project_list"), obj.pid, obj)


@admin_required
def projectquota_add(request, project_id):

    project = get_object_or_404(Project, pk=project_id)

    project_chunk = ProjectQuota()
    project_chunk.project = project

    form = ProjectQuotaForm(request.POST or None, instance=project_chunk)
    if request.method == 'POST':
        if form.is_valid():
            mc = form.cleaned_data['machine_category']
            conflicting = ProjectQuota.objects.filter(
                project=project,machine_category=mc)

            if conflicting.count() >= 1:
                form._errors["machine_category"] = util.ErrorList(["Cap already exists with this machine category"])
            else:
                project_chunk = form.save()
                new_cap = project_chunk.cap
                log(request.user, project, 2, 'Added cap of %s' % (new_cap))
                return HttpResponseRedirect(project.get_absolute_url())

    return render_to_response('projects/projectquota_form.html', locals(), context_instance=RequestContext(request))


@admin_required
def projectquota_edit(request, projectquota_id):

    project_chunk = get_object_or_404(ProjectQuota, pk=projectquota_id)
    old_cap = project_chunk.cap
    old_mc = project_chunk.machine_category

    form = ProjectQuotaForm(request.POST or None, instance=project_chunk)
    if request.method == 'POST':
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

    return render_to_response('projects/projectquota_form.html', locals(), context_instance=RequestContext(request))


@admin_required
def projectquota_delete(request, projectquota_id):

    project_chunk = get_object_or_404(ProjectQuota, pk=projectquota_id)

    if request.method == 'POST':
        project_chunk.delete()
        return HttpResponseRedirect(project_chunk.project.get_absolute_url())

    return render_to_response('projects/projectquota_delete_form.html', locals(), context_instance=RequestContext(request))


@admin_required
def projects_by_cap_used(request):
    from karaage.projects.views.admin import project_list
    return project_list(request, queryset=Project.active.all(), paginate=False, template_name='projects/project_capsort.html')
