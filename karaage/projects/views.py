# Copyright 2008-2015 VPAC
# Copyright 2010 The University of Melbourne
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

import six
import django_tables2 as tables

from django.forms.utils import ErrorList
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.db.models import Q
from django.contrib import messages
from django.core.urlresolvers import reverse

from karaage.common.decorators import admin_required, login_required
from karaage.people.models import Person
from karaage.machines.models import Account
from karaage.projects.tables import ProjectFilter, ProjectTable
from karaage.projects.models import Project, ProjectQuota
from karaage.projects.forms import ProjectForm, UserProjectForm, \
    ProjectQuotaForm, AddPersonForm
from karaage.projects.utils import get_new_pid, add_user_to_project, \
    remove_user_from_project
import karaage.common as util


@login_required
def profile_projects(request):
    config = tables.RequestConfig(request, paginate={"per_page": 5})

    person = request.user
    project_list = person.projects.all()
    project_list = ProjectTable(project_list, prefix="mine-")
    config.configure(project_list)

    delegate_project_list = Project.objects.filter(
        institute__delegates=person, is_active=True)
    delegate_project_list = ProjectTable(
        delegate_project_list, prefix="delegate-")
    config.configure(delegate_project_list)

    leader_project_list = Project.objects.filter(
        leaders=person, is_active=True)
    leader_project_list = ProjectTable(
        leader_project_list, prefix="leader-")
    config.configure(leader_project_list)

    return render_to_response(
        'karaage/projects/profile_projects.html',
        {'person': person, 'project_list': project_list,
            'delegate_project_list': delegate_project_list,
            'leader_project_list': leader_project_list},
        context_instance=RequestContext(request))


@login_required
def add_edit_project(request, project_id=None):

    if project_id is None:
        project = None
        old_pid = None
        flag = 1
    else:
        project = get_object_or_404(Project, id=project_id)
        old_pid = project.pid
        flag = 2

    if util.is_admin(request):
        form = ProjectForm(instance=project, data=request.POST or None)
    else:
        if not project.can_edit(request):
            return HttpResponseForbidden('<h1>Access Denied</h1>')
        form = UserProjectForm(instance=project, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            project = form.save(commit=False)
            if project_id is not None:
                # if project is being edited, project_id cannot change.
                project.pid = old_pid
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
                messages.success(
                    request, "Project '%s' created succesfully" % project)
            else:
                messages.success(
                    request, "Project '%s' edited succesfully" % project)

            return HttpResponseRedirect(project.get_absolute_url())

    return render_to_response(
        'karaage/projects/project_form.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def undelete_project(request, project_id):

    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        undeleted_by = request.user
        project.activate(undeleted_by)
        messages.success(
            request, "Project '%s' undeleted succesfully" % project)
        return HttpResponseRedirect(project.get_absolute_url())

    return render_to_response(
        'karaage/projects/project_confirm_undelete.html',
        {'project': project},
        context_instance=RequestContext(request))


@admin_required
def delete_project(request, project_id):

    project = get_object_or_404(Project, id=project_id)

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
        'karaage/projects/project_confirm_delete.html',
        {'project': project, 'error': error},
        context_instance=RequestContext(request))


@login_required
def project_detail(request, project_id):

    project = get_object_or_404(Project, id=project_id)

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
        'karaage/projects/project_detail.html',
        {'project': project, 'form': form,
            'can_edit': project.can_edit(request)},
        context_instance=RequestContext(request))


@admin_required
def project_verbose(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    from karaage.datastores import machine_category_get_project_details
    project_details = machine_category_get_project_details(project)

    return render_to_response(
        'karaage/projects/project_verbose.html',
        locals(),
        context_instance=RequestContext(request))


@login_required
def project_list(request, queryset=None):

    if queryset is None:
        queryset = Project.objects.all()

    if not util.is_admin(request):
        queryset = queryset.filter(
            Q(leaders=request.user, is_active=True) |
            Q(institute__delegates=request.user, is_active=True) |
            Q(group__members=request.user, is_active=True)).distinct()

    queryset = queryset.select_related()

    q_filter = ProjectFilter(request.GET, queryset=queryset)
    table = ProjectTable(q_filter.qs)
    tables.RequestConfig(request).configure(table)

    spec = []
    for name, value in six.iteritems(q_filter.form.cleaned_data):
        if value is not None and value != "":
            name = name.replace('_', ' ').capitalize()
            spec.append((name, value))

    return render_to_response(
        'karaage/projects/project_list.html',
        {
            'table': table,
            'filter': q_filter,
            'spec': spec,
            'title': "Project list",
        },
        context_instance=RequestContext(request))


@login_required
def remove_user(request, project_id, username):

    project = get_object_or_404(Project, id=project_id)
    person = get_object_or_404(Person, username=username)

    if not project.can_edit(request):
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
        'karaage/projects/remove_user_confirm.html',
        {'project': project, 'person': person, 'error': error, },
        context_instance=RequestContext(request))


@login_required
def grant_leader(request, project_id, username):
    project = get_object_or_404(Project, id=project_id)
    person = get_object_or_404(Person, username=username)

    if not project.can_edit(request):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    if project.group.members.filter(pk=person.pk).count() == 0:
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    if request.method == 'POST':
        if project.leaders.filter(pk=person.pk).count() == 0:
            project.leaders.add(person)
            messages.success(
                request,
                "User '%s' granted leader rights for project %s"
                % (person, project.pid))
        return HttpResponseRedirect(project.get_absolute_url())

    return render_to_response(
        'karaage/projects/grant_leader.html',
        {'project': project, 'person': person, },
        context_instance=RequestContext(request))


@login_required
def revoke_leader(request, project_id, username):
    project = get_object_or_404(Project, id=project_id)
    person = get_object_or_404(Person, username=username)

    if not project.can_edit(request):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    error = None
    if request.user == person:
        error = "Cannot revoke self."

    elif project.leaders.exclude(pk=person.pk).count() == 0:
        error = "Cannot revoke last project leader."

    elif request.method == 'POST':
        if project.leaders.filter(pk=person.pk).count() > 0:
            project.leaders.remove(person)
            messages.success(
                request,
                "User '%s' revoked leader rights for project %s"
                % (person, project.pid))
        return HttpResponseRedirect(project.get_absolute_url())

    return render_to_response(
        'karaage/projects/revoke_leader.html',
        {'project': project, 'person': person, 'error': error},
        context_instance=RequestContext(request))


@admin_required
def no_users(request):

    project_ids = []
    for p in Project.active.all():
        if p.group.members.count() == 0:
            project_ids.append(p.id)

    return project_list(request, Project.objects.filter(id__in=project_ids))


@admin_required
def project_logs(request, project_id):
    obj = get_object_or_404(Project, id=project_id)
    breadcrumbs = [
        ("Projects", reverse("kg_project_list")),
        (six.text_type(obj.pid), reverse("kg_project_detail", args=[obj.id]))
    ]
    return util.log_list(request, breadcrumbs, obj)


@admin_required
def add_comment(request, project_id):
    obj = get_object_or_404(Project, id=project_id)
    breadcrumbs = [
        ("Projects", reverse("kg_project_list")),
        (six.text_type(obj.pid), reverse("kg_project_detail", args=[obj.id]))
    ]
    return util.add_comment(request, breadcrumbs, obj)


@admin_required
def projectquota_add(request, project_id):

    project = get_object_or_404(Project, id=project_id)

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
        'karaage/projects/projectquota_form.html',
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
        'karaage/projects/projectquota_form.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def projectquota_delete(request, projectquota_id):

    project_chunk = get_object_or_404(ProjectQuota, pk=projectquota_id)

    if request.method == 'POST':
        project_chunk.delete()
        return HttpResponseRedirect(project_chunk.project.get_absolute_url())

    return render_to_response(
        'karaage/projects/projectquota_delete_form.html',
        locals(),
        context_instance=RequestContext(request))
