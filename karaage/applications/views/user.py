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
from django.conf import settings

import datetime

from karaage.applications.models import UserApplication, Applicant, Application
from karaage.applications.forms import UserApplicationForm, UserApplicantForm, LeaderUserApplicationForm
from karaage.applications.emails import send_account_request_email, send_account_approved_email
from karaage.people.models import Person
from karaage.projects.models import Project


def do_userapplication(request, token=None):
    if token:
        application = get_object_or_404(UserApplication, secret_token=token)
        if application.state not in (Application.NEW, Application.OPEN):
            raise Http404
        applicant = application.applicant
        application.state = Application.OPEN
        application.save()
    else:
        if not settings.ALLOW_REGISTRATIONS:
            return render_to_response('applications/registrations_disabled.html', {}, context_instance=RequestContext(request)) 
        application = None
        applicant = None
    if request.method == 'POST':
        form = UserApplicationForm(request.POST, instance=application)
        applicant_form = UserApplicantForm(request.POST, instance=applicant)
        if form.is_valid() and applicant_form.is_valid():
            applicant = applicant_form.save()
            application = form.save(commit=False)
            application.applicant = applicant
            application.save()
            if not application.project:
                return HttpResponseRedirect(reverse('kg_application_choose_project', args=[application.secret_token]))
            application.submitted_date = datetime.datetime.now()
            application.state = Application.WAITING_FOR_LEADER
            application.save()
            send_account_request_email(application)
            return HttpResponseRedirect(reverse('kg_application_done',  args=[application.secret_token]))
    else:
        form = UserApplicationForm(instance=application)
        applicant_form = UserApplicantForm(instance=applicant)
    
    return render_to_response('applications/userapplication_form.html', {'form': form, 'applicant_form': applicant_form, 'application': application}, context_instance=RequestContext(request)) 


def choose_project(request, token):
    application = get_object_or_404(UserApplication, secret_token=token)
    if application.state not in (Application.NEW, Application.OPEN):
            raise Http404
        
    institute = application.applicant.institute
    
    select_project_list = Project.objects.filter(institute=institute)
    
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
            q_project = Project.objects.get(pid__icontains=request.GET['leader_q'])
        except:
            pass
        leader_list = Person.projectleaders.filter(institute=institute)
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
        project_list = leader.leader.filter(is_active=True)

    if project_list:
        if project_list.count() == 1:
            project = project_list[0]
            project_list = False
                                   
    return render_to_response('applications/choose_project.html', locals(), context_instance=RequestContext(request))


def application_done(request, token):
    application = get_object_or_404(UserApplication, secret_token=token)
    if application.state in (Application.NEW, Application.OPEN):
        raise Http404

    return render_to_response('applications/done.html', {'application': application }, context_instance=RequestContext(request))


@login_required
def approve_userapplication(request, application_id):
    application = get_object_or_404(UserApplication, pk=application_id)
    if application.state != Application.WAITING_FOR_LEADER:
        raise Http404
    if not request.user.get_profile() in application.project.leaders.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    if request.method == 'POST':
        form = LeaderUserApplicationForm(request.POST, instance=application)
        if form.is_valid():
            application = form.save()

            needs_account_created = False
            if application.needs_account:
                for mc in application.project.machine_categories.all():
                    if not application.applicant.has_account(mc):
                        needs_account_created = True
                        break

            if needs_account_created and application.needs_account and settings.ADMIN_APPROVE_ACCOUNTS:
                application.state = Application.WAITING_FOR_ADMIN
                application.save()
                return HttpResponseRedirect(reverse('kg_userapplication_pending', args=[application.id]))

            application.approve()
            send_account_approved_email(application)
            return HttpResponseRedirect(reverse('kg_userapplication_complete', args=[application.id]))
    else:
        form = LeaderUserApplicationForm(instance=application)

    return render_to_response('applications/approve_application.html', {'form': form, 'application': application}, context_instance=RequestContext(request))


@login_required
def decline_userapplication(request, application_id):
    application = get_object_or_404(UserApplication, pk=application_id)
    if application.state != Application.WAITING_FOR_LEADER:
        raise Http404
    if not request.user.get_profile() in application.project.leaders.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>')
    
    if request.method == 'POST':
        send_account_rejected_email(application)
        
        application.delete()
        
        return HttpResponseRedirect(reverse('kg_user_profile'))

    return render_to_response('applications/confirm_decline.html', {'application': application}, context_instance=RequestContext(request))



@login_required
def userapplication_detail(request, application_id):
    application = get_object_or_404(UserApplication, pk=application_id)

    if application.state != Application.WAITING_FOR_LEADER:
        raise Http404
    if not request.user.get_profile() in application.project.leaders.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>')
    
    return render_to_response('applications/application_detail.html', {'application': application}, context_instance=RequestContext(request))

@login_required
def userapplication_complete(request, application_id):
    application = get_object_or_404(UserApplication, pk=application_id)
    if application.state != Application.COMPLETE:
        raise Http404
    if not request.user.get_profile() in application.project.leaders.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>') 

    return render_to_response('applications/userapplication_complete.html', {'application': application}, context_instance=RequestContext(request))

@login_required
def userapplication_pending(request, application_id):
    application = get_object_or_404(UserApplication, pk=application_id)
    if application.state != Application.WAITING_FOR_ADMIN:
        raise Http404
    if not request.user.get_profile() in application.project.leaders.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>') 

    return render_to_response('applications/userapplication_pending.html', {'application': application}, context_instance=RequestContext(request))


def application_index(request):
    if not settings.ALLOW_REGISTRATIONS:
        return render_to_response('applications/registrations_disabled.html', {}, context_instance=RequestContext(request)) 

    return render_to_response('applications/index.html', {}, context_instance=RequestContext(request))

