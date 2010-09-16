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
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages

from karaage.datastores import create_new_user
from karaage.people.models import Person
from karaage.projects.models import Project
from karaage.projects.utils import add_user_to_project
from karaage.util.email_messages import send_account_request_email, send_account_approved_email, send_account_rejected_email, send_project_join_approved_email
from karaage.util import log_object as log
from karaage.requests.models import ProjectJoinRequest
from karaage.requests.forms import UserRegistrationForm


def user_registration(request):
    """
    This is for a new user wanting to join a project

    """
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('user_choose_project'))

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save(request=request)
            return HttpResponseRedirect(reverse('user_choose_project'))
    else:
        form = UserRegistrationForm()

    return render_to_response('requests/user_request_form.html', { 'form': form, }, context_instance=RequestContext(request))


def choose_project(request):

    if request.user.is_authenticated():
        institute = request.user.get_profile().institute
    else:
        if not 'user_data' in request.session:
            return HttpResponseRedirect(reverse('user_registration'))
        
        institute = request.session['user_data']['institute']

    select_project_list = Project.objects.filter(institute=institute)
    
    project_list = False
    qs = request.META['QUERY_STRING']

    if request.method == 'POST':
        if request.REQUEST.has_key('project'):

            #  Store the request in the database
            project = Project.objects.get(pk=request.POST['project'])
            
            # If user is logged in ignore form and use original user
            if request.user.is_authenticated():
                person = request.user.get_profile()
            else:
                person = create_new_user(
                    request.session.get('user_data'), 
                    request.session['password']
                    )
            
            if person in project.users.all():
                error = 'Already in project'
                
                
            user_request = ProjectJoinRequest.objects.create(
                person=person,
                project=project,
                leader_approved=False,
                )
            
            if 'user_data' in request.session:
                del request.session['user_data']
            if 'password' in request.session:
                del request.session['password']
            if 'account' in request.session:
                del request.session['account']
            if 'project' in request.session:
                del request.session['project']
            
            # Send email to Project Leader for approval
            send_account_request_email(user_request)

            log(user_request.person.user, user_request.person, 1, 'Request for account and to join project %s' % user_request.project.pid)

            return HttpResponseRedirect(reverse('kg_user_account_pending', args=[user_request.id]))
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

                                        
    return render_to_response('requests/choose_project.html', locals(), context_instance=RequestContext(request))


def cancel_user_registration(request, user_request_id):
    user_request = get_object_or_404(ProjectJoinRequest, pk=user_request_id)

    person = user_request.person
    user = person.user

    
    if not user.is_active:
        user.delete()
        person.delete()
    user_request.delete()

    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('kg_user_profile')) 

    return HttpResponseRedirect(reverse('kg_user_index'))


def account_created(request, user_request_id):
    user_request = get_object_or_404(ProjectJoinRequest, pk=user_request_id)
    person = user_request.person
    project = user_request.project
    leader = project.leaders.all()[0]

    return render_to_response('requests/account_pending.html', locals(), context_instance=RequestContext(request))

@login_required
def approve_person(request, user_request_id):
    join_request = get_object_or_404(ProjectJoinRequest, pk=user_request_id)
    
    #Make sure the request is coming from the project leader
    if not request.user.get_profile() in join_request.project.leaders.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    join_request.leader_approved = True
    join_request.save()

    project = join_request.project
    person = join_request.person

    messages.info(request, "%s approved successfully" % person)
    
    log(request.user, person, 2, 'Approved by leader')

    needs_account_created = False
    for mc in project.machine_categories.all():
        if not person.has_account(mc):
            needs_account_created = True
            break
        
    if not needs_account_created:
        log(request.user, person, 2, 'Added to project %s' % project)
        log(request.user, project, 2, '%s added to project' % person)

        project.users.add(person)
        project.save()
        send_project_join_approved_email(join_request)
        join_request.delete()

        return HttpResponseRedirect(reverse('kg_user_profile'))

    if not settings.ADMIN_APPROVE_ACCOUNTS:

        person.activate()

        log(request.user, person, 2, 'Added to project %s' % project)
        log(request.user, project, 2, '%s added to project' % person)

        add_user_to_project(person, project)

        send_account_approved_email(join_request)
        join_request.delete()

    return HttpResponseRedirect(reverse('kg_user_profile')) 


@login_required
def reject_person(request, user_request_id):
    user_request = get_object_or_404(ProjectJoinRequest, pk=user_request_id)
    project = user_request.project
    person = user_request.person
    user = user_request.person.user
                                        
    if not request.user.get_profile() in project.leaders.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>')
    
    send_account_rejected_email(user_request)

    log(request.user, user_request.person, 3, 'Rejected by leader')
    
    if not person.is_active:
        person.delete()
        user.delete()
        
    user_request.delete()
           
    return HttpResponseRedirect(reverse('kg_user_profile'))


@login_required
def request_detail(request, user_request_id):

    
    user_request = get_object_or_404(ProjectJoinRequest, pk=user_request_id)

    project = user_request.project
    person = user_request.person

    if not request.user.get_profile() in project.leaders.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    
    return render_to_response('requests/user_request_detail.html', locals(), context_instance=RequestContext(request))
