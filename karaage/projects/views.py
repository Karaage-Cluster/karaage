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

from django.forms.util import ErrorList
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.core.urlresolvers import reverse

from karaage.common.filterspecs import Filter, FilterBar

from karaage.common.decorators import admin_required, login_required
from karaage.people.models import Person
from karaage.institutes.models import Institute
from karaage.machines.models import Account
from karaage.projects.models import Project, ProjectQuota
from karaage.projects.forms import ProjectForm, UserProjectForm, \
    ProjectQuotaForm, AddPersonForm
from karaage.projects.utils import add_user_to_project, \
    remove_user_from_project
import karaage.common as util


@login_required
def profile_projects(request):

    person = request.user
    project_list = person.projects.all()
    leader_project_list = []

    if person.is_leader():
        leader_project_list = Project.objects.filter(
            leaders=person, is_active=True)

    return render_to_response(
        'projects/profile_projects.html',
        {'person': person, 'project_list': project_list,
            'leader_project_list': leader_project_list},
        context_instance=RequestContext(request))


@login_required
def add_edit_project(request, project_id=None):

    if project_id is None:
        project = None
        flag = 1
    else:
        project = get_object_or_404(Project, pid=project_id)
        flag = 2

    if util.is_admin(request):
        form = ProjectForm(instance=project, data=request.POST or None)
    else:
        if project is None:
            return HttpResponseForbidden('<h1>Access Denied</h1>')
        if not request.user in project.leaders.all():
            return HttpResponseForbidden('<h1>Access Denied</h1>')
        form = UserProjectForm(instance=project, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            project = form.save()
            approved_by = request.user
            project.activate(approved_by)
            form.save_m2m()
            if flag == 1:
                messages.success(
                    request, "Project '%s' created succesfully" % project)
            else:
                messages.success(
                    request, "Project '%s' edited succesfully" % project)

            return HttpResponseRedirect(project.get_absolute_url())

    return render_to_response(
        'projects/project_form.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def delete_project(request, project_id):

    project = get_object_or_404(Project, pid=project_id)

    query = Account.objects.filter(
        date_deleted__isnull=True, default_project=project)

    error = None
    if query.count() > 0:
        error = "There are accounts that use this project " \
            "as the default_project."

    elif request.method == 'POST':
        deleted_by = request.user
        project.deactivate(deleted_by)
        messages.success(request, "Project '%s' deleted succesfully" % project)
        return HttpResponseRedirect(project.get_absolute_url())

    del query

    return render_to_response(
        'projects/project_confirm_delete.html',
        {'project': project, 'error': error},
        context_instance=RequestContext(request))


@login_required
def project_detail(request, project_id):

    project = get_object_or_404(Project, pid=project_id)

    if not project.can_view(request):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    form = AddPersonForm(request.POST or None)
    if request.method == 'POST':
        # Post means adding a user to this project
        if form.is_valid():
            person = form.cleaned_data['person']
            add_user_to_project(person, project)
            messages.success(
                request,
                "User '%s' was added to %s succesfully" % (person, project))
            return HttpResponseRedirect(project.get_absolute_url())

    return render_to_response(
        'projects/project_detail.html',
        {'project': project, 'form': form},
        context_instance=RequestContext(request))


@admin_required
def project_verbose(request, project_id):
    project = get_object_or_404(Project, pid=project_id)

    from karaage.datastores import machine_category_get_project_details
    project_details = machine_category_get_project_details(project)

    return render_to_response(
        'projects/project_verbose.html',
        locals(),
        context_instance=RequestContext(request))


@login_required
def project_list(request, queryset=None, template_name=None, paginate=True):

    if queryset is None:
        project_list = Project.objects.all()
    else:
        project_list = queryset

    if template_name is None:
        template_name = 'projects/project_list.html'

    project_list = project_list.select_related()

    if not util.is_admin(request):
        project_list = project_list.filter(group__members=request.user)

    if 'institute' in request.REQUEST:
        project_list = project_list.filter(
            institute=int(request.GET['institute']))

    if 'status' in request.REQUEST:
        project_list = project_list.filter(
            is_active=int(request.GET['status']))

    if 'search' in request.REQUEST:
        terms = request.REQUEST['search'].lower()
        query = Q()
        for term in terms.split(' '):
            query = Q(pid__icontains=term)
            query = query | Q(name__icontains=term)
            query = query | Q(description__icontains=term)
            query = query | Q(leaders__short_name__icontains=term)
            query = query | Q(leaders__full_name__icontains=term)
            query = query | Q(institute__name__icontains=term)
        project_list = project_list.filter(query).distinct()
    else:
        terms = ""

    filter_list = []
    filter_list.append(Filter(request, 'status', {1: 'Active', 0: 'Deleted'}))
    filter_list.append(Filter(request, 'institute', Institute.active.all()))
    filter_bar = FilterBar(request, filter_list)

    page_no = request.GET.get('page')
    if paginate:
        paginator = Paginator(project_list, 50)
    else:
        paginator = Paginator(project_list, 100000)

    # If page request (9999) is out of range, deliver last page of results.
    try:
        page = paginator.page(page_no)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page = paginator.page(paginator.num_pages)

    return render_to_response(
        template_name,
        {'page': page, 'filter_bar': filter_bar,
            'project_list': project_list, 'terms': terms},
        context_instance=RequestContext(request))


@login_required
def remove_user(request, project_id, username):

    project = get_object_or_404(Project, pid=project_id)
    person = get_object_or_404(Person, username=username)

    if not util.is_admin(request):
        if not request.user in project.leaders.all():
            return HttpResponseForbidden('<h1>Access Denied</h1>')

    query = person.account_set.filter(
        date_deleted__isnull=True, default_project=project)

    error = None
    if query.count() > 0:
        error = "The person has accounts that use this project " \
            "as the default_project."

    elif request.method == 'POST':
        remove_user_from_project(person, project)
        messages.success(
            request,
            "User '%s' removed succesfully from project %s"
            % (person, project.pid))
        return HttpResponseRedirect(project.get_absolute_url())

    del query

    return render_to_response(
        'projects/remove_user_confirm.html',
        {'project': project, 'person': person, 'error': error, },
        context_instance=RequestContext(request))


@admin_required
def no_users(request):

    project_ids = []
    for p in Project.active.all():
        if p.group.members.count() == 0:
            project_ids.append(p.pid)

    return project_list(request, Project.objects.filter(pid__in=project_ids))


@admin_required
def project_logs(request, project_id):
    obj = get_object_or_404(Project, pid=project_id)
    breadcrumbs = []
    breadcrumbs.append(
        ("Projects", reverse("kg_project_list")))
    breadcrumbs.append(
        (unicode(obj.pid), reverse("kg_project_detail", args=[obj.pid])))
    return util.log_list(request, breadcrumbs, obj)


@admin_required
def add_comment(request, project_id):
    obj = get_object_or_404(Project, pid=project_id)
    breadcrumbs = []
    breadcrumbs.append(
        ("Projects", reverse("kg_project_list")))
    breadcrumbs.append(
        (unicode(obj.pid), reverse("kg_project_detail", args=[obj.pid])))
    return util.add_comment(request, breadcrumbs, obj)


@admin_required
def projectquota_add(request, project_id):

    project = get_object_or_404(Project, pid=project_id)

    project_chunk = ProjectQuota()
    project_chunk.project = project

    form = ProjectQuotaForm(request.POST or None, instance=project_chunk)
    if request.method == 'POST':
        if form.is_valid():
            mc = form.cleaned_data['machine_category']
            conflicting = ProjectQuota.objects.filter(
                project=project, machine_category=mc)

            if conflicting.count() >= 1:
                form._errors["machine_category"] = \
                    ErrorList(
                        ["Cap already exists with this machine category"])
            else:
                project_chunk = form.save()
                new_cap = project_chunk.cap
                return HttpResponseRedirect(project.get_absolute_url())

    return render_to_response(
        'projects/projectquota_form.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def projectquota_edit(request, projectquota_id):

    project_chunk = get_object_or_404(ProjectQuota, pk=projectquota_id)
    old_mc = project_chunk.machine_category

    form = ProjectQuotaForm(request.POST or None, instance=project_chunk)
    if request.method == 'POST':
        if form.is_valid():
            mc = form.cleaned_data['machine_category']
            if old_mc.pk != mc.pk:
                form._errors["machine_category"] = ErrorList([
                    "Please don't change the machine category; "
                    "it confuses me"])
            else:
                project_chunk = form.save()
                return HttpResponseRedirect(
                    project_chunk.project.get_absolute_url())

    return render_to_response(
        'projects/projectquota_form.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def projectquota_delete(request, projectquota_id):

    project_chunk = get_object_or_404(ProjectQuota, pk=projectquota_id)

    if request.method == 'POST':
        project_chunk.delete()
        return HttpResponseRedirect(project_chunk.project.get_absolute_url())

    return render_to_response(
        'projects/projectquota_delete_form.html',
        locals(),
        context_instance=RequestContext(request))
