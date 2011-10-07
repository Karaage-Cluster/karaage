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
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from django.core.paginator import Paginator
from django.core.mail import send_mail

import datetime
from django_shibboleth.utils import ensure_shib_session, build_shib_url
from andsome.forms import EmailForm

from karaage.applications.models import UserApplication, ProjectApplication, Applicant, Application
from karaage.applications.forms import UserApplicationForm, UserApplicantForm, LeaderApproveUserApplicationForm, LeaderInviteUserApplicationForm, StartApplicationForm, StartInviteApplicationForm
from karaage.applications.emails import send_account_request_email, send_account_approved_email, send_user_invite_email, send_notify_admin, render_email
from karaage.applications.saml import SAMLApplicantForm, get_saml_user, add_saml_data
from karaage.people.models import Person
from karaage.projects.models import Project
from karaage.datastores import create_password_hash
from karaage.util import log_object as log



def do_userapplication(request, token=None, saml=False, 
                       application_form=UserApplicationForm):
    if request.user.is_authenticated():
        messages.warning(request, "You are already logged in")
        return HttpResponseRedirect(reverse('kg_user_profile'))

    if saml:
        response = ensure_shib_session(request)
        if response:
            return response

    if token:
        try:
            application = UserApplication.objects.get(
                                        secret_token=token, 
                                        state__in=[Application.NEW, Application.OPEN],
                                        expires__gt=datetime.datetime.now())
        except UserApplication.DoesNotExist:
            return render_to_response('applications/old_userapplication.html',
                                        {'help_email': settings.ACCOUNTS_EMAIL,},
                                        context_instance=RequestContext(request))
        applicant = application.applicant
        application.state = Application.OPEN
        application.save()
        captcha = False
    else:
        if not settings.ALLOW_REGISTRATIONS:
            return render_to_response('applications/registrations_disabled.html', {}, context_instance=RequestContext(request)) 
        application = UserApplication()
        applicant = None
        captcha = True
    if saml:
        captcha = False
        saml_user = get_saml_user(request)
    else:
        saml_user = None

    if application.content_type and application.content_type.model == 'person':
        return existing_user_application(request, token)
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
                applicant.email_verified = True
            applicant.password = create_password_hash(applicant_form.cleaned_data['password1'])
            applicant.save()
            application = form.save(commit=False)
            application.applicant = applicant
            application.save()
            if not application.project:
                application.state = Application.OPEN
                application.save()
                return HttpResponseRedirect(reverse('kg_application_choose_project', args=[application.secret_token]))
            application.submitted_date = datetime.datetime.now()
            application.state = Application.WAITING_FOR_LEADER
            application.save()
            send_account_request_email(application)
            return HttpResponseRedirect(reverse('kg_application_done',  args=[application.secret_token]))
    else:
        form = application_form(instance=application, captcha=captcha)
        if saml:
            applicant_form = SAMLApplicantForm(instance=applicant)
        else:
            applicant_form = UserApplicantForm(instance=applicant, initial={'institute': init_institute})
    return render_to_response('applications/userapplication_form.html', 
                              {'form': form, 'applicant_form': applicant_form, 'application': application, 
                               'saml': saml, 'saml_user': saml_user, }, 
                              context_instance=RequestContext(request)) 


def existing_user_application(request, token):
    
    application = get_object_or_404(UserApplication, 
                                    secret_token=token, 
                                    state__in=[Application.NEW, Application.OPEN],
                                    expires__gt=datetime.datetime.now())

    if request.method == 'POST':
        application.submitted_date = datetime.datetime.now()
        application.state = Application.WAITING_FOR_LEADER
        application.save()
        send_account_request_email(application)
        return HttpResponseRedirect(reverse('kg_application_done',  args=[application.secret_token]))
    
    return render_to_response('applications/existing_user_confirm.html', {'application': application}, context_instance=RequestContext(request)) 


def choose_project(request, token=None):
    if request.user.is_authenticated():
        application = UserApplication()
        application.applicant = request.user.get_profile()
    else:
        application = get_object_or_404(UserApplication, 
                                        secret_token=token, 
                                        state__in=[Application.NEW, Application.OPEN], 
                                        expires__gt=datetime.datetime.now())

    institute = application.applicant.institute
    
    project_list = False
    qs = request.META['QUERY_STRING']

    if request.method == 'POST':
        if request.REQUEST.has_key('project'):
            project = Project.objects.get(pk=request.POST['project'])
            application.project = project
            application.state = Application.WAITING_FOR_LEADER
            application.submitted_date = datetime.datetime.now()
            application.needs_account = True
            application.save()
            send_account_request_email(application)

            return HttpResponseRedirect(reverse('kg_application_done',  args=[application.secret_token]))
        else:
            return HttpResponseRedirect('%s?%s&error=true' % (reverse('user_choose_project'), qs))

    if request.REQUEST.has_key('error'):
        project_error = True
    
    if request.REQUEST.has_key('leader_q'):
        q_project = False
        try:
            q_project = Project.active.get(pid__icontains=request.GET['leader_q'])
        except:
            pass
        leader_list = Person.active.filter(institute=institute, leaders__isnull=False).distinct()
        terms = request.GET['leader_q'].lower()
        length = len(terms)
        if len(terms) >= 3:
            query = Q()
            for term in terms.split(' '):
                q = Q(user__username__icontains=term) | Q(user__first_name__icontains=term) | Q(user__last_name__icontains=term) 
                query = query & q
            leader_list = leader_list.filter(query)
            if leader_list.count() == 1:
                leader = leader_list[0]
                project_list = leader.leaders.filter(is_active=True)
                leader_list = False
            elif leader_list.count() == 0 and not q_project:
                term_error = "No projects found."
        else:
            term_error = "Please enter at lease three characters for search."
            leader_list = False
    if request.REQUEST.has_key('leader'):
        leader = Person.objects.get(pk=request.GET['leader'])
        project_list = leader.leaders.filter(is_active=True)

    if project_list:
        if project_list.count() == 1:
            project = project_list[0]
            project_list = False
                                   
    return render_to_response('applications/choose_project.html', locals(), context_instance=RequestContext(request))


def application_done(request, token):
    application = get_object_or_404(Application, secret_token=token)
    application = application.get_object()
    if application.state in (Application.NEW, Application.OPEN):
        return HttpResponseForbidden('<h1>Access Denied</h1>')
    return render_to_response('%s/%s_done.html' % (application._meta.app_label, application._meta.object_name.lower()), {'application': application }, context_instance=RequestContext(request))


@login_required
def approve_userapplication(request, application_id):
    application = get_object_or_404(UserApplication, pk=application_id)
    if not request.user.get_profile() in application.project.leaders.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>')
    if application.state != Application.WAITING_FOR_LEADER:
        return render_to_response('applications/unable_to_approve.html', {'application': application }, context_instance=RequestContext(request))

    if request.method == 'POST':
        form = LeaderApproveUserApplicationForm(request.POST, instance=application)
        if form.is_valid():
            application = form.save()

            if settings.ADMIN_APPROVE_ACCOUNTS:
                application.state = Application.WAITING_FOR_ADMIN
                application.save()
                send_notify_admin(application)
                log(request.user, application.application_ptr, 2, 'Leader approved application')
                return HttpResponseRedirect(reverse('kg_userapplication_pending', args=[application.id]))

            application.approve()
            send_account_approved_email(application)
            log(request.user, application.application_ptr, 2, 'Application fully approved')
            return HttpResponseRedirect(reverse('kg_userapplication_complete', args=[application.id]))
    else:
        form = LeaderApproveUserApplicationForm(instance=application)

    return render_to_response('applications/approve_application.html', {'form': form, 'application': application}, context_instance=RequestContext(request))


@login_required
def decline_userapplication(request, application_id):
    application = get_object_or_404(UserApplication, pk=application_id)
    if not request.user.get_profile() in application.project.leaders.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>')
    if application.state != Application.WAITING_FOR_LEADER:
        return render_to_response('applications/unable_to_approve.html', {'application': application }, context_instance=RequestContext(request))

    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            to_email = application.applicant.email
            subject, body = form.get_data()
            log(request.user, application.application_ptr, 3, "Application declined")
            application.delete()        
            send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)
            return HttpResponseRedirect(reverse('kg_user_profile'))
    else:
        subject, body = render_email('account_declined', { 'receiver': application.applicant, 'project': application.project })
        initial_data = {'body': body, 'subject': subject,}
        form = EmailForm(initial=initial_data)
    
    return render_to_response('applications/confirm_decline.html', {'application': application, 'form': form}, context_instance=RequestContext(request))



@login_required
def userapplication_detail(request, application_id):
    application = get_object_or_404(UserApplication, pk=application_id)

    if not request.user.get_profile() in application.project.leaders.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>')
    if application.state != Application.WAITING_FOR_LEADER:
        return render_to_response('applications/unable_to_approve.html', {'application': application }, context_instance=RequestContext(request))

    if application.state != Application.WAITING_FOR_LEADER:
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    return render_to_response('applications/application_detail.html', {'application': application}, context_instance=RequestContext(request))

@login_required
def userapplication_complete(request, application_id):
    application = get_object_or_404(UserApplication, pk=application_id)
    if application.state != Application.COMPLETE:
        return HttpResponseForbidden('<h1>Access Denied</h1>')
    if not request.user.get_profile() in application.project.leaders.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>') 
    
    return render_to_response('applications/userapplication_complete.html', {'application': application}, context_instance=RequestContext(request))

@login_required
def userapplication_pending(request, application_id):
    application = get_object_or_404(UserApplication, pk=application_id)
    if application.state != Application.WAITING_FOR_ADMIN:
        return HttpResponseForbidden('<h1>Access Denied</h1>')
    if not request.user.get_profile() in application.project.leaders.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>') 

    return render_to_response('applications/userapplication_pending.html', {'application': application}, context_instance=RequestContext(request))


def application_index(request):
    if not settings.ALLOW_REGISTRATIONS:
        return render_to_response('applications/registrations_disabled.html', {}, context_instance=RequestContext(request))

    if request.method == 'POST':
        form = StartApplicationForm(request.POST)
        if form.is_valid():
            institute = form.cleaned_data['institute']
            app_type = form.cleaned_data['application_type']
            if app_type == 'U':
                if institute.saml_entityid:
                    return HttpResponseRedirect(build_shib_url(
                            request, reverse('kg_saml_new_userapplication'), institute.saml_entityid))
                else:
                    return HttpResponseRedirect(reverse('kg_new_userapplication') + '?institute=%s' % institute.id)
            elif app_type == 'P':
                if institute.saml_entityid:
                    return HttpResponseRedirect(build_shib_url(
                            request, reverse('kg_saml_new_projectapplication'), institute.saml_entityid))

                else:
                    return HttpResponseRedirect(reverse('kg_new_projectapplication') + '?institute=%s' % institute.id)
    else:
        form = StartApplicationForm()

    return render_to_response('applications/index.html', {'form': form}, context_instance=RequestContext(request))


@login_required
def send_invitation(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if not request.user.get_profile() in project.leaders.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>')
    application = None

    if request.method == 'POST':
        form = LeaderInviteUserApplicationForm(request.POST, instance=application)

        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                existing = Person.active.get(user__email=email)
            except Person.DoesNotExist:
                existing = False
            if existing and not request.REQUEST.has_key('existing'):
                return render_to_response('applications/userapplication_invite_existing.html', 
                                          {'form': form, 'person': existing}, 
                                          context_instance=RequestContext(request))
            application = form.save(commit=False)

            try:
                applicant = Person.active.get(user__email=email)
            except Person.DoesNotExist:
                applicant, created = Applicant.objects.get_or_create(email=email)

            application.applicant = applicant
            application.project = project
            application.save()
            if application.content_type.model == 'person':
                application.approve()
                send_account_approved_email(application)
                messages.warning(request, "%s was added to project %s directly since they have an existing account." % 
                              (application.applicant, application.project))
                log(request.user, application.application_ptr, 1, "%s added directly to %s" % (applicant, project))
                return HttpResponseRedirect(application.applicant.get_absolute_url())

            send_user_invite_email(application)
            messages.success(request, "Invitation sent to %s." % email)
            log(request.user, application.application_ptr, 1, 'Invitation sent')
            return HttpResponseRedirect(reverse('kg_user_profile'))
        
    else:
        form = LeaderInviteUserApplicationForm(instance=application)

    return render_to_response('applications/leaderuserapplication_invite_form.html', 
                              {'form': form, 'application': application, 'project': project}, 
                              context_instance=RequestContext(request)) 

@login_required
def pending_applications(request):
    person = request.user.get_profile()
    page_no = int(request.GET.get('page', 1))
    user_applications = UserApplication.objects.filter(project__in=person.leaders.all())
    project_applications = ProjectApplication.objects.filter(institute__in=person.delegate.all())
    p = Paginator(user_applications, 50)
    projects_p = Paginator(project_applications, 50)
    page = p.page(page_no)
    projects_page = projects_p.page(page_no)
    return render_to_response('applications/pending_application_list.html', 
                              {'user_applications': user_applications, 'page': page,
                               'project_applications': project_applications, 'projects_page': projects_page},
                              context_instance=RequestContext(request)) 



def start_invite_application(request, token):
    try:
        application = Application.objects.get(
            secret_token=token, 
            state__in=[Application.NEW, Application.OPEN],
            expires__gt=datetime.datetime.now())
    except Application.DoesNotExist:
        return render_to_response('applications/old_userapplication.html',
                                  {'help_email': settings.ACCOUNTS_EMAIL,},
                                  context_instance=RequestContext(request))

    if request.method == 'POST':
        form = StartInviteApplicationForm(request.POST)
        if form.is_valid():
            institute = form.cleaned_data['institute']
            application.state = Application.OPEN
            application.save()
            if institute.saml_entityid:
                return HttpResponseRedirect(build_shib_url(
                        request, reverse('kg_saml_invited_userapplication', args=[application.secret_token]),
                        institute.saml_entityid))
            else:
                return HttpResponseRedirect(reverse('kg_invited_userapplication', args=[application.secret_token]) + '?institute=%s' % institute.id)
    else:
        form = StartInviteApplicationForm()

    return render_to_response('applications/start_invite.html', {'form': form}, context_instance=RequestContext(request))


def cancel(request, token):    
    
    application = get_object_or_404(Application,
                                    secret_token=token, 
                                    state__in=[Application.NEW, Application.OPEN],
                                    expires__gt=datetime.datetime.now())
    if request.method == 'POST':
        application.delete()
        return HttpResponseRedirect(reverse('index'))

    return render_to_response('applications/cancel.html', {'application': application}, context_instance=RequestContext(request))

