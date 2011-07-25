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
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.mail import send_mail
from django.conf import settings

from andsome.util.filterspecs import Filter, FilterBar
from andsome.forms import EmailForm

from karaage.people.models import Person
from karaage.applications.models import UserApplication, ProjectApplication, Applicant, Application
from karaage.applications.forms import AdminInviteUserApplicationForm, ApplicantForm, LeaderApproveUserApplicationForm, AdminApproveProjectApplicationForm
from karaage.applications.emails import send_user_invite_email, send_account_approved_email, send_project_approved_email, render_email
from karaage.util import log_object as log


@permission_required('applications.add_userapplication')
def send_invitation(request):

    application = None

    if request.method == 'POST':
        form = AdminInviteUserApplicationForm(request.POST, instance=application)

        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                existing = Person.active.get(user__email=email)
            except Person.DoesNotExist:
                existing = False
            if existing and not request.REQUEST.has_key('existing'):
                return render_to_response(
                    'applications/userapplication_invite_existing.html', 
                    {'form': form, 'person': existing}, context_instance=RequestContext(request)) 
            application = form.save(commit=False)
            try:
                applicant = Person.active.get(user__email=email)
            except Person.DoesNotExist:
                applicant, created = Applicant.objects.get_or_create(email=email)

            application.applicant = applicant
            application.save()
            if application.content_type.model == 'person':
                application.approve()
                messages.info(request, "%s was added to project %s directly since they have an existing account." % (application.applicant, application.project))
                log(request.user, application.application_ptr, 1, "%s added directly to %s" % (application.applicant, application.project))
                send_account_approved_email(application)
                return HttpResponseRedirect(application.applicant.get_absolute_url())
            send_user_invite_email(application)
            messages.info(request, "Invitation sent to %s." % email)
            log(request.user, application.application_ptr, 1, 'Invitation sent')
            return HttpResponseRedirect(application.get_absolute_url())
        
    else:
        form = AdminInviteUserApplicationForm(instance=application)

    return render_to_response('applications/userapplication_invite_form.html', {'form': form, 'application': application}, context_instance=RequestContext(request)) 


@login_required
def application_list(request):

    apps = Application.objects.select_related().order_by('-id')

    try:
        page_no = int(request.GET.get('page', 1))
    except ValueError:
        page_no = 1

    if request.REQUEST.has_key('state'):
        apps = apps.filter(state=request.GET['state'])

    if request.REQUEST.has_key('search'):
        terms = request.REQUEST['search'].lower()
        query = Q()
        for term in terms.split(' '):
            q = Q(created_by__user__first_name__icontains=term) | Q(created_by__user__last_name__icontains=term)
            query = query & q

        apps = apps.filter(query)
    else:
        terms = ""

    filter_list = []
    filter_list.append(Filter(request, 'state', Application.APPLICATION_STATES))
    filter_bar = FilterBar(request, filter_list)

    p = Paginator(apps, 50)

    try:
        page = p.page(page_no)
    except (EmptyPage, InvalidPage):
        page = p.page(p.num_pages)

    return render_to_response('applications/application_list.html', {'page': page, 'filter_bar': filter_bar}, context_instance=RequestContext(request))


@permission_required('applications.change_application')
def approve_userapplication(request, application_id):
    application = get_object_or_404(UserApplication, pk=application_id)

    if application.state != Application.WAITING_FOR_ADMIN:
        raise Http404

    if request.method == 'POST':
        form = LeaderApproveUserApplicationForm(request.POST, instance=application)
        if form.is_valid():
            application = form.save()
            person = application.approve()
            send_account_approved_email(application)
            messages.info(request, "Application approved successfully")
            log(request.user, application.application_ptr, 2, 'Application fully approved')
            return HttpResponseRedirect(person.get_absolute_url())
    else:
        form = LeaderApproveUserApplicationForm(instance=application)

    return render_to_response('applications/approve_application.html', {'form': form, 'application': application}, context_instance=RequestContext(request))


@permission_required('applications.delete_application')
def decline_userapplication(request, application_id):
    application = get_object_or_404(UserApplication, pk=application_id)

    if application.state != Application.WAITING_FOR_ADMIN:
        raise Http404
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            to_email = application.applicant.email
            subject, body = form.get_data()
            log(request.user, application.application_ptr, 3, 'Application declined')
            messages.info(request, "%s declined successfully." % application)
            application.delete()
            send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)
            return HttpResponseRedirect(reverse('kg_application_list'))
    else:
        subject, body = render_email('account_declined', { 'receiver': application.applicant, 'project': application.project })
        initial_data = {'body': body, 'subject': subject,}
        form = EmailForm(initial=initial_data)

    return render_to_response('applications/confirm_decline.html', {'application': application, 'form': form}, context_instance=RequestContext(request))


@permission_required('applications.change_application')
def approve_projectapplication(request, application_id):
    application = get_object_or_404(ProjectApplication, pk=application_id)

    if application.state != Application.WAITING_FOR_ADMIN:
        raise Http404

    if request.method == 'POST':
        form = AdminApproveProjectApplicationForm(request.POST, instance=application)
        if form.is_valid():
            application = form.save()
            project = application.approve(pid=form.cleaned_data['pid'])
            send_project_approved_email(application)
            messages.info(request, "Application approved successfully.")
            log(request.user, application.application_ptr, 2, 'Application fully approved')
            return HttpResponseRedirect(project.get_absolute_url())
    else:
        form = AdminApproveProjectApplicationForm(instance=application)

    return render_to_response('applications/approve_projectapplication.html', {'form': form, 'application': application}, context_instance=RequestContext(request))


@permission_required('applications.delete_application')
def decline_projectapplication(request, application_id):
    application = get_object_or_404(ProjectApplication, pk=application_id)

    if application.state != Application.WAITING_FOR_ADMIN:
        raise Http404
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            to_email = application.applicant.email
            subject, body = form.get_data()
            log(request.user, application.application_ptr, 3, 'Application declined')
            messages.info(request, "%s declined successfully." % application)
            application.delete()
            send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)
            return HttpResponseRedirect(reverse('kg_application_list'))

    else:
        subject, body = render_email('project_declined', { 'receiver': application.applicant })
        initial_data = {'body': body, 'subject': subject,}
        form = EmailForm(initial=initial_data)

    return render_to_response('applications/project_confirm_decline.html', {'application': application, 'form': form}, context_instance=RequestContext(request))



@login_required
def application_detail(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    application = application.get_object()
    return render_to_response('%s/%s_admindetail.html' % (application._meta.app_label, application._meta.object_name.lower()), {'application': application }, context_instance=RequestContext(request))


@permission_required('applications.delete_application')
def delete_application(request, application_id):
    application = get_object_or_404(Application, pk=application_id)

    if request.method == 'POST':
        application.delete()
        log(request.user, application, 3, 'Application deleted')
        messages.info(request, "%s deleted successfully." % application)
        return HttpResponseRedirect(reverse('kg_application_list'))

    return render_to_response('applications/application_confirm_delete.html', {'application': application}, context_instance=RequestContext(request))


@permission_required('applications.change_application')
def archive_application(request, application_id):
    application = get_object_or_404(Application, pk=application_id)

    if request.method == 'POST':
        application.state = Application.ARCHIVED
        application.save()
        log(request.user, application, 2, 'Application archived')
        messages.info(request, "%s archived successfully." % application)
        return HttpResponseRedirect(application.get_absolute_url())

    return render_to_response('applications/application_archive.html', {'application': application}, context_instance=RequestContext(request))

@permission_required('applications.change_applicant')
def applicant_edit(request, applicant_id):
    
    applicant = get_object_or_404(Applicant, id=applicant_id)

    if request.method == 'POST':
        form = ApplicantForm(request.POST, instance=applicant)
        if form.is_valid():
            applicant = form.save()
            log(request.user, applicant, 2, 'Edited')
            messages.info(request, "%s modified successfully." % applicant)
            try:
                return HttpResponseRedirect(applicant.applications.all()[0].get_absolute_url())
            except IndexError:
                return HttpResponseRedirect(reverse('kg_application_list'))
    else:
        form = ApplicantForm(instance=applicant)
    
    return render_to_response('applications/applicant_form.html', {'applicant': applicant, 'form': form}, context_instance=RequestContext(request)) 
