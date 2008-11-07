from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.conf import settings

import datetime

from karaage.datastores import create_new_user
from karaage.people.models import Person
from karaage.requests.models import UserRequest
from karaage.projects.models import Project
from karaage.machines.models import MachineCategory
from karaage.util.email_messages import *
from karaage.requests.forms import UserRegistrationForm
#from accounts.ajabber.jab import send_jab
#from accounts.util.shib import get_shib_attrs
from karaage.util import log_object as log


def user_registration(request):
    """
    This is for a new user wanting to join a project

    """
    from random import choice
    import Image, ImageDraw, ImageFont, sha
    import os
    SALT = settings.SECRET_KEY[:20]
    imgtext = ''.join([choice('QWERTYUPASDFGHJKLZXCVBNM') for i in range(5)])
 
    im = Image.open('%s/img/captcha_bg.jpg' % settings.MEDIA_ROOT)
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(settings.CAPTCHA_FONT, 18)
    draw.text((10,10), imgtext, font=font, fill=(100,100,50))

    temp = '%s/img/captcha/user_%s.jpg' % (settings.MEDIA_ROOT, request.META.get('REMOTE_ADDR', 'unknown'))
    tempname = 'user_' + request.META.get('REMOTE_ADDR', 'unknown') + '.jpg'
    im.save(temp, "JPEG")

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save(request=request)
            os.remove('%s/img/captcha/user_%s.jpg' % (settings.MEDIA_ROOT, request.META.get('REMOTE_ADDR', 'unknown')))
            return HttpResponseRedirect(reverse('user_choose_project'))
    else:
        form = UserRegistrationForm()
        #form.initial = get_shib_attrs(request.META)


    imghash = sha.new(SALT+imgtext).hexdigest()

    return render_to_response('requests/user_request_form.html', { 'form': form, 'tempname': tempname, 'imghash': imghash }, context_instance=RequestContext(request))


def choose_project(request):
    session = request.session
    if request.user.is_authenticated():
        institute = request.user.get_profile().institute
    else:
        institute = request.session['user_data']['institute']
                                        

    project_list = False
    qs = request.META['QUERY_STRING']

    if request.method == 'POST':
        if request.REQUEST.has_key('project'):

            #  Store the request in the database
            project = Project.objects.get(pk=request.POST['project'])
            
            # If user is logged in ignore form and use origional user
            if request.user.is_authenticated():
                person = request.user.get_profile()
            else:
                person = create_new_user(
                    request.session.get('user_data'), 
                    request.session['password']
                    )
            
            user_request = UserRequest.objects.create(
                person=person,
                project=project,
                machine_category=MachineCategory.objects.get_default(),
                leader_approved=False,
                needs_account=request.session.get('account', True)
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

            return HttpResponseRedirect(reverse('user_account_created', args=[user_request.id]))
        else:
            return HttpResponseRedirect('%s?%s&error=true' % (reverse('user_choose_project'), qs))

                                        
    if request.REQUEST.has_key('error'):
        project_error = True
    
    if request.REQUEST.has_key('leader_q'):
        q_project = False
        try:
            test = request.GET['leader_q'][7]
            q_project = Project.objects.get(pid__icontains=request.GET['leader_q'])
        except:
            pass
        leader_list = Person.leaders.filter(institute=institute)
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
                project_list = leader.leader.filter(is_active=True)
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
    user_request = get_object_or_404(UserRequest, pk=user_request_id)

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
    user_request = get_object_or_404(UserRequest, pk=user_request_id)
    person = user_request.person
    project = user_request.project
    machine_category = user_request.machine_category
    
    return render_to_response('requests/account_pending.html', locals(), context_instance=RequestContext(request))

@login_required
def approve_person(request, user_request_id):
    user_request = get_object_or_404(UserRequest, pk=user_request_id)
    
    #Make sure the request is coming from the project leader
    if not request.user == user_request.project.leader.user:
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    user_request.leader_approved = True
    user_request.save()

    request.user.message_set.create(message="%s approved successfully" % user_request.person)
    
    log(request.user, user_request.person, 2, 'Approved by leader')

    if user_request.person.has_account(user_request.machine_category):
        log(request.user, user_request.person, 2, 'Added to project %s' % user_request.project)
        log(request.user, user_request.project, 2, '%s added to project' % user_request.person)

        user_request.project.users.add(user_request.person)
        send_project_join_approved_email(user_request)
        user_request.person.user.message_set.create(message="Your request to join the project %s has been accepted" % user_request.project.pid)
        user_request.delete()
    else:
        pass
        #send_jab('sam@vpac.org', 'Accounts', 'There is a new account waiting for approval')

    return HttpResponseRedirect(reverse('kg_user_profile')) 


@login_required
def reject_person(request, user_request_id):
    user_request = get_object_or_404(UserRequest, pk=user_request_id)
    project = user_request.project
    person = user_request.person
    user = user_request.person.user
                                        
    if not request.user == project.leader.user:
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

    
    user_request = get_object_or_404(UserRequest, pk=user_request_id)

    project = user_request.project
    person = user_request.person

    if not request.user.get_profile() == project.leader:
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    
    return render_to_response('requests/user_request_detail.html', locals(), context_instance=RequestContext(request))
