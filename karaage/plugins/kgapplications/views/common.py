# Copyright 2015 VPAC
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
import datetime

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect

from karaage.common.decorators import admin_required, login_required
import karaage.common as util

from ..tables import ApplicationFilter, ApplicationTable
from ..models import Applicant, Application
from ..forms import ApplicantForm

from . import base


@login_required
def application_list(request):
    """ a user wants to see all applications possible. """

    if util.is_admin(request):
        queryset = Application.objects.all()
    else:
        queryset = Application.objects.get_for_applicant(request.user)

    q_filter = ApplicationFilter(request.GET, queryset=queryset)

    table = ApplicationTable(q_filter.qs.order_by("-expires"))
    tables.RequestConfig(request).configure(table)

    spec = []
    for name, value in six.iteritems(q_filter.form.cleaned_data):
        if value is not None and value != "":
            name = name.replace('_', ' ').capitalize()
            spec.append((name, value))

    return render_to_response(
        "kgapplications/application_list.html",
        {
            'table': table,
            'filter': q_filter,
            'spec': spec,
            'title': "Application list",
        },
        context_instance=RequestContext(request))


@login_required
def profile_application_list(request):
    """ a logged in user wants to see all his pending applications. """
    config = tables.RequestConfig(request, paginate={"per_page": 5})

    person = request.user
    my_applications = Application.objects.get_for_applicant(person)
    my_applications = ApplicationTable(my_applications, prefix="mine-")
    config.configure(my_applications)

    requires_attention = Application.objects.requires_attention(request)
    requires_attention = ApplicationTable(requires_attention, prefix="attn-")
    config.configure(requires_attention)

    return render_to_response(
        'kgapplications/profile_applications.html',
        {
            'person': request.user,
            'my_applications': my_applications,
            'requires_attention': requires_attention,
        },
        context_instance=RequestContext(request))


@admin_required
def applicant_edit(request, applicant_id):
    applicant = get_object_or_404(Applicant, id=applicant_id)

    form = ApplicantForm(request.POST or None, instance=applicant)
    if request.method == 'POST':
        if form.is_valid():
            applicant = form.save()
            messages.success(request, "%s modified successfully." % applicant)
            return HttpResponseRedirect(reverse('kg_application_list'))

    return render_to_response(
        'kgapplications/applicant_form.html',
        {'form': form}, context_instance=RequestContext(request))


@admin_required
def application_logs(request, application_id):
    obj = get_object_or_404(Application, pk=application_id)
    breadcrumbs = [
        ("Applications", reverse("kg_application_list")),
        (six.text_type(obj), reverse("kg_application_detail", args=[obj.pk]))
    ]
    return util.log_list(request, breadcrumbs, obj)


@admin_required
def add_comment(request, application_id):
    obj = get_object_or_404(Application, pk=application_id)
    breadcrumbs = [
        ("Applications", reverse("kg_application_list")),
        (six.text_type(obj), reverse("kg_application_detail", args=[obj.pk]))
    ]
    return util.add_comment(request, breadcrumbs, obj)


@login_required
def application_detail(request, application_id, state=None, label=None):
    """ A authenticated used is trying to access an application. """
    application = base.get_application(pk=application_id)
    state_machine = base.get_state_machine(application)
    return state_machine.process(request, application, state, label)


def application_unauthenticated(request, token, state=None, label=None):
    """ An somebody is trying to access an application. """
    application = base.get_application(secret_token=token)
    if application.expires < datetime.datetime.now():
        return render_to_response(
            'kgapplications/common_expired.html',
            {'application': application},
            context_instance=RequestContext(request))

    roles = {'is_applicant', 'is_authorised'}

    # redirect user to real url if possible.
    if request.user.is_authenticated():
        if request.user == application.applicant:
            url = base.get_url(
                request, application, roles, label)
            return HttpResponseRedirect(url)

    state_machine = base.get_state_machine(application)
    return state_machine.process(
        request, application, state, label, roles)
