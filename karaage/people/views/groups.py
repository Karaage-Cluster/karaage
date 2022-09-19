# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
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
import six
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

import karaage.common as util
from karaage.common.decorators import admin_required
from karaage.people.forms import AddGroupMemberForm, AdminGroupForm
from karaage.people.models import Group, Person
from karaage.people.tables import GroupFilter, GroupTable


@admin_required
def group_list(request):
    queryset = Group.objects.select_related()

    q_filter = GroupFilter(request.GET, queryset=queryset)
    table = GroupTable(q_filter.qs)
    tables.RequestConfig(request).configure(table)

    spec = []
    for name, value in six.iteritems(q_filter.form.cleaned_data):
        if value is not None and value != "":
            name = name.replace("_", " ").capitalize()
            spec.append((name, value))

    return render(
        template_name="karaage/people/group_list.html",
        context={
            "table": table,
            "filter": q_filter,
            "spec": spec,
            "title": "Group list",
        },
        request=request,
    )


def _add_edit_group(request, form_class, group_name):
    group_form = form_class

    if group_name is None:
        group = None
    else:
        group = get_object_or_404(Group, name=group_name)

    if request.method == "POST":
        form = group_form(request.POST, instance=group)
        if form.is_valid():
            if group:
                # edit
                group = form.save()
                messages.success(request, "Group '%s' was edited succesfully" % group)
            else:
                # add
                group = form.save()
                messages.success(request, "Group '%s' was created succesfully" % group)

            return HttpResponseRedirect(group.get_absolute_url())
    else:
        form = group_form(instance=group)

    return render(
        template_name="karaage/people/group_form.html", context={"group": group, "form": form}, request=request
    )


@admin_required
def add_group(request):
    return _add_edit_group(request, AdminGroupForm, None)


@admin_required
def edit_group(request, group_name):
    return _add_edit_group(request, AdminGroupForm, group_name)


@admin_required
def delete_group(request, group_name):
    group = get_object_or_404(Group, name=group_name)

    error = None

    if group.institute_set.all().count() > 0:
        error = "An institute is using this group."
    elif group.project_set.all().count() > 0:
        error = "A project is using this group."
    elif request.method == "POST":
        group.delete()
        messages.success(request, "Group '%s' was deleted succesfully" % group)
        return HttpResponseRedirect(reverse("kg_group_list"))

    return render(template_name="karaage/people/group_confirm_delete.html", context=locals(), request=request)


@admin_required
def group_detail(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    form = AddGroupMemberForm(instance=group)

    return render(template_name="karaage/people/group_detail.html", context=locals(), request=request)


@admin_required
def group_verbose(request, group_name):
    group = get_object_or_404(Group, name=group_name)

    from karaage.datastores import get_group_details

    group_details = get_group_details(group)

    return render(template_name="karaage/people/group_verbose.html", context=locals(), request=request)


@admin_required
def group_logs(request, group_name):
    obj = get_object_or_404(Group, name=group_name)
    breadcrumbs = [
        ("Groups", reverse("kg_group_list")),
        (six.text_type(obj), reverse("kg_group_detail", args=[obj.name])),
    ]
    return util.log_list(request, breadcrumbs, obj)


@admin_required
def add_comment(request, group_name):
    obj = get_object_or_404(Group, name=group_name)
    breadcrumbs = [
        ("Groups", reverse("kg_group_list")),
        (six.text_type(obj), reverse("kg_group_detail", args=[obj.name])),
    ]
    return util.add_comment(request, breadcrumbs, obj)


@admin_required
def add_group_member(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    if request.method == "POST":
        form = AddGroupMemberForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(group.get_absolute_url())
    else:
        form = AddGroupMemberForm(instance=group)

    return render(template_name="karaage/people/group_add_member.html", context=locals(), request=request)


@admin_required
def remove_group_member(request, group_name, username):
    group = get_object_or_404(Group, name=group_name)
    person = get_object_or_404(Person, username=username)

    error = None
    for account in person.account_set.filter(date_deleted__isnull=True):
        # Does the default_project for ua belong to this group?
        count = group.project_set.filter(pk=account.default_project.pk).count()
        # If yes, error
        if count > 0:
            error = "The person has accounts that use this group as the default_project."

    if error is None and request.method == "POST":
        group.remove_person(person)
        return HttpResponseRedirect(group.get_absolute_url())

    return render(template_name="karaage/people/group_remove_member.html", context=locals(), request=request)
