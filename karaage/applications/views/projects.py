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
from django.conf import settings
from django.core.mail import send_mail

import datetime
from django_shibboleth.utils import ensure_shib_session
from andsome.forms import EmailForm

from karaage.applications.models import ProjectApplication, Application
from karaage.applications.forms import ProjectApplicationForm, UserApplicantForm, ApproveProjectApplicationForm
from karaage.applications.emails import send_project_request_email, send_project_approved_email, send_notify_admin, render_email
from karaage.applications.saml import SAMLApplicantForm, get_saml_user, add_saml_data
from karaage.machines.models import MachineCategory
from karaage.util import log_object as log


def do_projectapplication(request, token=None, application_form=ProjectApplicationForm, 
                          mc=MachineCategory.objects.get_default(), saml=False):

    if request.user.is_authenticated():
        messages.info(request, "You are already logged in")
        return HttpResponseRedirect(reverse('kg_user_profile'))

    if saml:
        response = ensure_shib_session(request)
        if response:
            return response

    if token:
        application = get_object_or_404(ProjectApplication, secret_token=token)
        if application.state not in (Application.NEW, Application.OPEN):
            raise Http404
        applicant = application.applicant
        application.state = Application.OPEN
        application.save()
        captcha = False
    else:
        if not settings.ALLOW_REGISTRATIONS:
            return render_to_response('applications/registrations_disabled.html', {}, context_instance=RequestContext(request)) 
        application = None
        applicant = None
        captcha = True

    if saml:
        captcha = False
        saml_user = get_saml_user(request)
    else:
        saml_user = None
    init_institute = request.GET.get('institute', '')
    if request.method == 'POST':
        form = application_form(request.POST, instance=application, captcha=captcha)
        if saml:
            applicant_form = SAMLApplicantForm(request.POST, instance=applicant)
        else:
            applicant_form = UserApplicantForm(request.POST, instance=applicant)

        if form.is_valid() and applicant_form.is_valid():
            applicant = applicant_form.save(commit=False)
            if saml:
                applicant = add_saml_data(applicant, request)
            applicant.save()
            application = form.save(commit=False)
            application.applicant = applicant
            application.submitted_date = datetime.datetime.now()
            application.state = Application.WAITING_FOR_DELEGATE
            application.save()
            application.machine_categories.add(mc)
            send_project_request_email(application)
            return HttpResponseRedirect(reverse('kg_application_done',  args=[application.secret_token]))
    else:
        form = application_form(instance=application, captcha=captcha, initial={'institute': init_institute})
        if saml:
            applicant_form = SAMLApplicantForm(instance=applicant)
        else:
            applicant_form = UserApplicantForm(instance=applicant, initial={'institute': init_institute})
    
    return render_to_response('applications/projectapplication_form.html', {'form': form, 'applicant_form': applicant_form, 
                                                                            'application': application, 'saml': saml,
                                                                            'saml_user': saml_user, }, 
                              context_instance=RequestContext(request)) 


@login_required
def approve_projectapplication(request, application_id):
    application = get_object_or_404(ProjectApplication, pk=application_id)
    if not request.user.get_profile() == application.institute.delegate:
        return HttpResponseForbidden('<h1>Access Denied</h1>')
    if application.state != Application.WAITING_FOR_DELEGATE:
        return render_to_response('applications/unable_to_approve.html', {'application': application }, context_instance=RequestContext(request))

    if request.method == 'POST':
        form = ApproveProjectApplicationForm(request.POST, instance=application)
        if form.is_valid():
            application = form.save()

            if settings.ADMIN_APPROVE_ACCOUNTS:
                application.state = Application.WAITING_FOR_ADMIN
                application.save()
                #send_notify_admin(application, request.user.get_full_name())
                log(request.user, application, 2, 'Delegate approved application')
                return HttpResponseRedirect(reverse('kg_projectapplication_pending', args=[application.id]))

            application.approve()
            send_project_approved_email(application)
            log(request.user, application, 2, 'Delegate fully approved')
            return HttpResponseRedirect(reverse('kg_projectapplication_complete', args=[application.id]))
    else:
        form = ApproveProjectApplicationForm(instance=application)

    return render_to_response('applications/projectapplication_approve.html', {'form': form, 'application': application}, context_instance=RequestContext(request))


@login_required
def projectapplication_pending(request, application_id):
    application = get_object_or_404(ProjectApplication, pk=application_id)
    if application.state != Application.WAITING_FOR_ADMIN:
        return HttpResponseForbidden('<h1>Access Denied</h1>')
    if not request.user.get_profile() == application.institute.delegate:
        return HttpResponseForbidden('<h1>Access Denied</h1>') 
    
    return render_to_response('applications/projectapplication_pending.html', {'application': application}, context_instance=RequestContext(request))



@login_required
def projectapplication_complete(request, application_id):
    application = get_object_or_404(ProjectApplication, pk=application_id)
    if application.state != Application.COMPLETE:
        return HttpResponseForbidden('<h1>Access Denied</h1>')
    if not request.user.get_profile() == application.institute.delegate:
        return HttpResponseForbidden('<h1>Access Denied</h1>') 
    
    return render_to_response('applications/projectapplication_complete.html', {'application': application}, context_instance=RequestContext(request))


@login_required
def projectapplication_existing(request, application_form=ProjectApplicationForm, mc=MachineCategory.objects.get_default()):

    application = ProjectApplication()
    applicant = request.user.get_profile()
    init_institute = request.GET.get('institute', '')

    if request.method == 'POST':
        form = application_form(request.POST, instance=application)

        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = applicant
            application.save()
            application.submitted_date = datetime.datetime.now()
            application.state = Application.WAITING_FOR_DELEGATE
            application.save()
            application.machine_categories.add(mc)
            send_project_request_email(application)
            return HttpResponseRedirect(reverse('kg_application_done',  args=[application.secret_token]))
    else:
        form = application_form(instance=application, initial={'institute': init_institute})
    
    return render_to_response('applications/projectapplication_existing_form.html', {'form': form, 'application': application}, context_instance=RequestContext(request)) 


def decline_projectapplication(request, application_id):
    application = get_object_or_404(ProjectApplication, pk=application_id)

    if not request.user.get_profile() == application.institute.delegate:
        return HttpResponseForbidden('<h1>Access Denied</h1>')
    
    if application.state != Application.WAITING_FOR_DELEGATE:
        return render_to_response('applications/unable_to_approve.html', {'application': application }, context_instance=RequestContext(request))

    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            to_email = application.applicant.email
            subject, body = form.get_data()
            log(request.user, application, 3, 'Application declined')
            application.delete()
            send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)
            return HttpResponseRedirect(reverse('kg_application_pendinglist'))

    else:
        subject, body = render_email('project_declined', { 'receiver': application.applicant })
        initial_data = {'body': body, 'subject': subject,}
        form = EmailForm(initial=initial_data)

    return render_to_response('applications/project_confirm_decline.html', {'application': application, 'form': form}, context_instance=RequestContext(request))
