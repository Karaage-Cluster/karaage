# Copyright 2008, 2010-2011, 2013-2015 VPAC
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
import datetime

import django_tables2 as tables

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden, \
    HttpResponseBadRequest
from django.http import QueryDict
from django.contrib import messages
from django.core.urlresolvers import reverse

from karaage.common.decorators import admin_required, login_required
from karaage.people.tables import PersonFilter, PersonTable, LeaderTable
from karaage.people.models import Person
from karaage.people.emails import send_bounced_warning
from karaage.people.emails import send_reset_password_email
from karaage.people.forms import AddPersonForm, AdminPersonForm
from karaage.people.forms import AdminPasswordChangeForm
from karaage.projects.models import Project
from karaage.projects.tables import ProjectTable
from karaage.institutes.tables import InstituteTable

import karaage.common as common


def _add_edit_user(request, form_class, username):
    person_form = form_class

    if username is None:
        person = None
    else:
        person = get_object_or_404(Person, username=username)

    form = person_form(request.POST or None, instance=person)
    if request.method == 'POST':
        if form.is_valid():
            if person:
                # edit
                person = form.save()
                messages.success(
                    request, "User '%s' was edited succesfully" % person)
                assert person is not None
            else:
                # add
                person = form.save()
                messages.success(
                    request, "User '%s' was created succesfully" % person)
                assert person is not None

            return HttpResponseRedirect(person.get_absolute_url())

    return render_to_response(
        'karaage/people/person_form.html',
        {'person': person, 'form': form},
        context_instance=RequestContext(request))


@admin_required
def add_user(request):
    return _add_edit_user(request, AddPersonForm, None)


@admin_required
def edit_user(request, username):
    return _add_edit_user(request, AdminPersonForm, username)


@login_required
def user_list(request, queryset=None, title=None):
    if queryset is None:
        queryset = Person.objects.all()

    if not common.is_admin(request):
        queryset = queryset.filter(pk=request.user.pk)

    queryset = queryset.select_related()

    q_filter = PersonFilter(request.GET, queryset=queryset)

    table = PersonTable(q_filter.qs)
    tables.RequestConfig(request).configure(table)

    spec = []
    for name, value in six.iteritems(q_filter.form.cleaned_data):
        if value is not None and value != "":
            name = name.replace('_', ' ').capitalize()
            spec.append((name, value))

    context = {
        'table': table,
        'filter': q_filter,
        'spec': spec,
        'title': title or "Person list",
    }

    return render_to_response(
        "karaage/people/person_list.html", context,
        context_instance=RequestContext(request))


@admin_required
def locked_list(request):

    result = QueryDict("", mutable=True)
    result['active'] = "locked"
    url = reverse('kg_person_list') + "?" + result.urlencode()
    return HttpResponseRedirect(url)


@admin_required
def struggling(request):
    today = datetime.date.today()
    days30 = today - datetime.timedelta(days=30)

    result = QueryDict("", mutable=True)
    result['active'] = "yes"
    result['begin_date_approved'] = days30
    result['no_last_usage'] = True
    result['sort'] = "-date_approved"
    url = reverse('kg_person_list') + "?" + result.urlencode()
    return HttpResponseRedirect(url)


@admin_required
def delete_user(request, username):

    person = get_object_or_404(Person, username=username)

    if request.method == 'POST':
        deleted_by = request.user
        person.deactivate(deleted_by)
        messages.success(request, "User '%s' was deleted succesfully" % person)
        return HttpResponseRedirect(person.get_absolute_url())

    return render_to_response(
        'karaage/people/person_confirm_delete.html', locals(),
        context_instance=RequestContext(request))


@login_required
def user_detail(request, username):
    config = tables.RequestConfig(request, paginate={"per_page": 5})

    person = get_object_or_404(Person, username=username)
    if not person.can_view(request):
        return HttpResponseForbidden(
            '<h1>Access Denied</h1>'
            '<p>You do not have permission to view details '
            'about this person.</p>')

    leader_project_list = Project.objects.filter(
        leaders=person, is_active=True)
    leader_project_list = ProjectTable(
        leader_project_list, prefix="leader-")
    config.configure(leader_project_list)

    delegate_institute_list = person.delegate_for.all()
    delegate_institute_list = delegate_institute_list.select_related()
    delegate_institute_list = InstituteTable(
        delegate_institute_list, prefix="delegate")
    config.configure(delegate_institute_list)

    return render_to_response(
        'karaage/people/person_detail.html', locals(),
        context_instance=RequestContext(request))


@admin_required
def user_verbose(request, username):
    person = get_object_or_404(Person, username=username)

    from karaage.datastores import global_get_person_details
    person_details = global_get_person_details(person)

    from karaage.datastores import machine_category_get_account_details
    account_details = []
    for ua in person.account_set.filter(date_deleted__isnull=True):
        details = machine_category_get_account_details(ua)
        account_details.append(details)

    return render_to_response(
        'karaage/people/person_verbose.html', locals(),
        context_instance=RequestContext(request))


@admin_required
def activate(request, username):
    person = get_object_or_404(Person, username=username)

    if person.is_active:
        return HttpResponseBadRequest("<h1>Bad Request</h1>")

    if request.method == 'POST':
        approved_by = request.user
        person.activate(approved_by)
        return HttpResponseRedirect(
            reverse('kg_person_password', args=[person.username]))

    return render_to_response(
        'karaage/people/person_reactivate.html',
        {'person': person},
        context_instance=RequestContext(request))


@admin_required
def password_change(request, username):
    person = get_object_or_404(Person, username=username)

    if request.POST:
        form = AdminPasswordChangeForm(data=request.POST, person=person)

        if form.is_valid():
            form.save()
            messages.success(request, "Password changed successfully")
            if person.is_locked():
                person.unlock()
            return HttpResponseRedirect(person.get_absolute_url())
    else:
        form = AdminPasswordChangeForm(person=person)

    return render_to_response(
        'karaage/people/person_password.html',
        {'person': person, 'form': form},
        context_instance=RequestContext(request))


@admin_required
def lock_person(request, username):
    person = get_object_or_404(Person, username=username)

    if request.method == 'POST':
        person.lock()
        messages.success(request, "%s's account has been locked" % person)
        return HttpResponseRedirect(person.get_absolute_url())

    return render_to_response(
        'karaage/people/person_confirm_lock.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def unlock_person(request, username):
    person = get_object_or_404(Person, username=username)
    if request.method == 'POST':
        person.unlock()
        messages.success(request, "%s's account has been unlocked" % person)
        return HttpResponseRedirect(person.get_absolute_url())
    return render_to_response(
        'karaage/people/person_confirm_unlock.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def bounced_email(request, username):
    person = get_object_or_404(Person, username=username)

    leader_list = []
    for project in person.projects.filter(is_active=True):
        for leader in project.leaders.filter(
                is_active=True, login_enabled=True):
            leader_list.append({'project': project, 'leader': leader})

    if request.method == 'POST':
        person.lock()
        send_bounced_warning(person, leader_list)
        messages.success(
            request,
            "%s's account has been locked and emails have been sent" % person)
        common.log.change(
            person,
            'Emails sent to project leaders and account locked')
        return HttpResponseRedirect(person.get_absolute_url())

    leader_list = LeaderTable(leader_list)
    tables.RequestConfig(request).configure(leader_list)

    return render_to_response(
        'karaage/people/person_bounced_email.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def person_logs(request, username):
    obj = get_object_or_404(Person, username=username)
    breadcrumbs = [
        ("People", reverse("kg_person_list")),
        (six.text_type(obj), reverse("kg_person_detail", args=[obj.username]))
    ]
    return common.log_list(request, breadcrumbs, obj)


@admin_required
def add_comment(request, username):
    obj = get_object_or_404(Person, username=username)
    breadcrumbs = [
        ("People", reverse("kg_person_list")),
        (six.text_type(obj), reverse("kg_person_detail", args=[obj.username]))
    ]
    return common.add_comment(request, breadcrumbs, obj)


@login_required
def password_request(request, username):
    person = get_object_or_404(Person, username=username)
    error = None

    post_reset_redirect = reverse(
        'kg_person_reset_done', args=[person.username])

    if not person.can_view(request):
        return HttpResponseForbidden(
            '<h1>Access Denied</h1>'
            '<p>You do not have permission to view details '
            'about this user.</p>')

    elif not person.is_active:
        error = "Person '%s' is deleted." % person.username

    elif not person.login_enabled:
        error = "Person '%s' is locked." % person.username

    elif request.method == "POST":
        send_reset_password_email(person)
        return HttpResponseRedirect(post_reset_redirect)

    var = {
        'person': person,
        'error': error,
    }
    return render_to_response(
        'karaage/people/person_password_request.html',
        var,
        context_instance=RequestContext(request))


@login_required
def password_request_done(request, username):
    person = get_object_or_404(Person, username=username)

    if not person.can_view(request):
        return HttpResponseForbidden(
            '<h1>Access Denied</h1>'
            '<p>You do not have permission to view details '
            'about this user.</p>')

    var = {
        'person': person,
    }
    return render_to_response(
        'karaage/people/person_password_request_done.html',
        var,
        context_instance=RequestContext(request))
