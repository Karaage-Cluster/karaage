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

import datetime

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect

from karaage.common.decorators import admin_required, login_required
from karaage.applications.models import Applicant, Application
from karaage.applications.forms import ApplicantForm
import karaage.applications.views.base as base
from karaage.common import log
import karaage.common as util

@login_required
def application_list(request):
    """ a logged in user wants to see all his pending applications. """
    person = request.user
    applications = Application.objects.all()

    if not util.is_admin(request):
        applications = Application.objects.get_for_applicant(request.user)


    if 'search' in request.REQUEST:
        terms = request.REQUEST['search'].lower()
        query = Q()

        if terms:
            for term in terms.split(' '):
                q = Q(projectapplication__project__pid__icontains=term)
                q = q | Q(projectapplication__project__name__icontains=term)
                q = q | Q(softwareapplication__software_license__software__name__icontains=term)
                query = query & q

        applications = applications.filter(query)
    else:
        terms = ""

    page_no = request.GET.get('page')
    paginator = Paginator(applications, 50)
    try:
        page = paginator.page(page_no)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page = paginator.page(paginator.num_pages)

    return render_to_response(
        "applications/application_list.html",
        {'page': page, 'terms': terms},
        context_instance=RequestContext(request))

@login_required
def profile_application_list(request):
    """ a logged in user wants to see all his pending applications. """
    person = request.user
    my_applications = Application.objects.get_for_applicant(person)
    requires_attention = Application.objects.requires_attention(request)

    return render_to_response(
            'applications/profile_applications.html',
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

    return render_to_response('applications/applicant_form.html',
            {'form': form}, context_instance=RequestContext(request))


@admin_required
def application_logs(request, application_id):
    obj = get_object_or_404(Application, pk=application_id)
    breadcrumbs = []
    breadcrumbs.append( ("Applications", reverse("kg_application_list")) )
    breadcrumbs.append( (unicode(obj), reverse("kg_application_detail", args=[obj.pk])) )
    return util.log_list(request, breadcrumbs, obj)


@admin_required
def add_comment(request, application_id):
    obj = get_object_or_404(Application, pk=application_id)
    breadcrumbs = []
    breadcrumbs.append( ("Applications", reverse("kg_application_list")) )
    breadcrumbs.append( (unicode(obj), reverse("kg_application_detail", args=[obj.pk])) )
    return util.add_comment(request, breadcrumbs, obj)


@login_required
def application_detail(request, application_id, state=None, label=None):
    """ A authenticated used is trying to access an application. """
    application = base.get_application(pk=application_id)
    state_machine = base.get_state_machine(application)
    return state_machine.process(request, application, state, label)

def application_unauthenticated(request, token, state=None, label=None):
    """ An somebody is trying to access an application. """
    application = base.get_application(
                secret_token=token, expires__gt=datetime.datetime.now())

    # redirect user to real url if possible.
    if request.user.is_authenticated():
        if request.user == application.applicant:
            url = base.get_url(request, application, {'is_applicant': True}, label)
            return HttpResponseRedirect(url)

    state_machine = base.get_state_machine(application)
    return state_machine.process(request, application, state, label,
            { 'is_applicant': True })

