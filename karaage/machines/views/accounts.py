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

from django.contrib import messages
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

import karaage.common as common
from karaage.common.decorators import admin_required, login_required
from karaage.machines.forms import (
    AddProjectForm,
    AdminAccountForm,
    UserAccountForm,
)
from karaage.machines.models import Account
from karaage.people.models import Person
from karaage.people.views.persons import user_list
from karaage.projects.models import Project
from karaage.projects.utils import add_user_to_project


@login_required
def profile_accounts(request):
    person = request.user
    accounts = person.account_set.filter(date_deleted__isnull=True)
    return render(template_name="karaage/machines/profile_accounts.html", context=locals(), request=request)


@admin_required
def add_account(request, username=None):
    person = get_object_or_404(Person, username=username)
    account = None

    form = AdminAccountForm(data=request.POST or None, instance=account, person=person, initial={"username": username})

    if request.method == "POST":
        if form.is_valid():
            account = form.save()
            person = account.person
            return HttpResponseRedirect(person.get_absolute_url())

    return render(
        template_name="karaage/machines/account_form.html",
        context={"form": form, "person": person, "account": account},
        request=request,
    )


@login_required
def account_detail(request, account_id):
    account = get_object_or_404(Account, pk=account_id)

    if not account.can_view(request):
        return HttpResponseForbidden(
            "<h1>Access Denied</h1><p>You do not have permission to view details about this account.</p>"
        )

    return render(
        template_name="karaage/machines/account_detail.html",
        context={"account": account, "can_edit": account.can_edit(request)},
        request=request,
    )


@login_required
def edit_account(request, account_id):
    account = get_object_or_404(Account, pk=account_id)

    if not account.can_edit(request):
        return HttpResponseForbidden(
            "<h1>Access Denied</h1><p>You do not have permission to edit details of this account.</p>"
        )

    if common.is_admin(request):
        person = account.person
        username = account.username
        form = AdminAccountForm(
            data=request.POST or None, instance=account, person=person, initial={"username": username}
        )
    else:
        person = request.user
        assert account.person == person
        form = UserAccountForm(data=request.POST or None, instance=account)

    if request.method == "POST":
        if form.is_valid():
            account = form.save()
            person = account.person
            return HttpResponseRedirect(person.get_absolute_url())

    return render(
        template_name="karaage/machines/account_form.html",
        context={"form": form, "person": person, "account": account},
        request=request,
    )


@admin_required
def add_project(request, username):
    person = get_object_or_404(Person, username=username)

    # Add to project form
    form = AddProjectForm(request.POST or None)
    if request.method == "POST":
        # Post means adding this user to a project
        if form.is_valid():
            project = form.cleaned_data["project"]
            add_user_to_project(person, project)
            messages.success(request, "User '%s' was added to %s succesfully" % (person, project))
            return HttpResponseRedirect(person.get_absolute_url())

    return render(template_name="karaage/machines/person_add_project.html", context=locals(), request=request)


@admin_required
def delete_account(request, account_id):

    account = get_object_or_404(Account, pk=account_id)

    if request.method == "POST":
        account.deactivate()
        messages.success(request, "User account for '%s' deleted succesfully" % account.person)
        return HttpResponseRedirect(account.get_absolute_url())

    return render(template_name="karaage/machines/account_confirm_delete.html", context=locals(), request=request)


@admin_required
def no_project_list(request):
    persons = Person.active.filter(groups__project__isnull=True, account__isnull=False)
    return user_list(request, persons, "No projects")


@admin_required
def no_default_list(request):
    persons = Person.objects.filter(
        account__isnull=False, account__default_project__isnull=True, account__date_deleted__isnull=True
    )
    return user_list(request, persons, "No default projects")


@admin_required
def no_account_list(request):
    person_id_list = []

    for u in Person.objects.all():
        if not u.has_account():
            person_id_list.append(u.id)

    persons = Person.objects.filter(id__in=person_id_list)
    return user_list(request, persons, "No accounts")


@admin_required
def wrong_default_list(request):
    wrong = []
    for u in Person.active.all():
        for ua in u.account_set.filter(date_deleted__isnull=True):
            d = False
            for p in ua.project_list():
                if p == ua.default_project:
                    d = True
            if not d:
                if not u.is_locked():
                    wrong.append(u.id)

    persons = Person.objects.filter(id__in=wrong)
    return user_list(request, persons, "Wrong default projects")


@login_required
def make_default(request, account_id, project_id):
    account = get_object_or_404(Account, pk=account_id)
    redirect = reverse("kg_account_detail", args=[account.pk])

    if not account.can_edit(request):
        return HttpResponseForbidden(
            "<h1>Access Denied</h1><p>You do not have permission to edit details of this account.</p>"
        )

    try:
        project = account.person.projects.get(pid=project_id)
    except Project.DoesNotExist:
        return HttpResponseForbidden("<h1>Access Denied</h1><p>Person owning account is not in this project.</p>")

    if request.method != "POST":
        return HttpResponseBadRequest("<h1>Bad Request</h1>")

    account.default_project = project
    account.save()
    messages.success(request, "Default project changed succesfully")

    return HttpResponseRedirect(redirect)
