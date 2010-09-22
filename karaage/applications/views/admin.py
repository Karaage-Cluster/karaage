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
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import permission_required, login_required
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from andsome.util.filterspecs import Filter, FilterBar

from karaage.applications.models import UserApplication, Applicant, Application
from karaage.applications.forms import AdminUserApplicationForm as UserApplicationForm, ApplicantForm
from karaage.applications.emails import send_user_invite_email


@permission_required('applications.add_userapplication')
def add_edit_userapplication(request, application_id=None):
    
    if application_id:
        application = get_object_or_404(UserApplication, pk=application_id)
        applicant = application.applicant
    else:
        application = None
        applicant = None

    if request.method == 'POST':
        form = UserApplicationForm(request.POST, instance=application)
        applicant_form = ApplicantForm(request.POST, instance=applicant)

        if form.is_valid() and applicant_form.is_valid():
            applicant = applicant_form.save()
            application = form.save(commit=False)
            application.applicant = applicant
            application.save()
            send_user_invite_email(application)
            return HttpResponseRedirect(application.get_absolute_url())
        
    else:
        form = UserApplicationForm(instance=application)
        applicant_form = ApplicantForm(instance=applicant)

    return render_to_response('applications/admin_userapplication_form.html', {'form': form, 'applicant_form': applicant_form, 'application': application}, context_instance=RequestContext(request)) 

@login_required
def application_list(request, queryset=UserApplication.objects.select_related().all(), template_name='applications/application_list.html', paginate=True):

    querystring = request.META.get('QUERY_STRING', '')

    apps = queryset

    page_no = int(request.GET.get('page', 1))

    if request.REQUEST.has_key('state'):
        apps = apps.filter(state=request.GET['state'])

    if request.method == 'POST':
        new_data = request.POST.copy()
        terms = new_data['search'].lower()
        query = Q()
        for term in terms.split(' '):
            q = Q(created_by__user__first_name__icontains=term) | Q(created_by__user__last_name__icontains=term) | Q(project__icontains=term)
            query = query & q

        apps = apps.filter(query)
    else:
        terms = ""

    filter_list = []
    filter_list.append(Filter(request, 'state', UserApplication.APPLICATION_STATES))
    filter_bar = FilterBar(request, filter_list)

    if paginate:
        p = Paginator(apps, 50)
        page = p.page(page_no)
    else:
        p = Paginator(apps, 100000)
        page = p.page(page_no)

    return render_to_response(template_name, {'page':page, 'filter_bar':filter_bar}, context_instance=RequestContext(request))

@login_required
def approve_userapplication(request, application_id):
    application = get_object_or_404(UserApplication, pk=application_id)

    if request.method == 'POST':
        form = LeaderUserApplicationForm(request.POST, instance=application)
        if form.is_valid():
            application = form.save()

            application.approve()
            send_account_approved_email(application)
            return HttpResponseRedirect(reverse('kg_userapplication_complete', args=[application.id]))
    else:
        form = LeaderUserApplicationForm(instance=application)

    return render_to_response('applications/approve_application.html', {'form': form, 'application': application}, context_instance=RequestContext(request))


@login_required
def decline_userapplication(request, application_id):
    application = get_object_or_404(UserApplication, pk=application_id)

    if request.method == 'POST':
        send_account_rejected_email(application)

        application.delete()

        return HttpResponseRedirect(reverse('kg_user_profile'))

    return render_to_response('applications/confirm_decline.html', {'application': application}, context_instance=RequestContext(request))

@login_required
def userapplication_detail(request, application_id):
    application = get_object_or_404(UserApplication, pk=application_id)

    return render_to_response('applications/adminapplication_detail.html', {'application': application}, context_instance=RequestContext(request))

@login_required
def userapplication_complete(request, application_id):
    application = get_object_or_404(UserApplication, pk=application_id)

    return render_to_response('applications/userapplication_complete.html', {'application': application}, context_instance=RequestContext(request))

