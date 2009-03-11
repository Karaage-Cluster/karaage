from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

import datetime

from karaage.requests.models import ProjectCreateRequest, ProjectJoinRequest
from karaage.projects.models import Project
from karaage.projects.util import add_user_to_project
from karaage.machines.models import MachineCategory
from karaage.requests.forms import ProjectRegistrationForm
from karaage.util.email_messages import *
from karaage.util import log_object as log

# Create your views here.
def project_registration(request):
    """
    This is for a new user wanting to start a project
    
    """
    from random import choice
    import Image, ImageDraw, ImageFont, sha
    import os
    SALT = settings.SECRET_KEY[:20]
    imgtext = ''.join([choice('QWERTYUOPASDFGHJKLZXCVBNM') for i in range(5)])
 
    im = Image.open('%s/img/captcha_bg.jpg' % settings.MEDIA_ROOT)
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(settings.CAPTCHA_FONT, 18)
    draw.text((10,10), imgtext, font=font, fill=(100,100,50))

    temp = '%s/img/captcha/project_%s.jpg' % (settings.MEDIA_ROOT, request.META.get('REMOTE_ADDR', 'unknown'))
    tempname = 'project_' + request.META.get('REMOTE_ADDR', 'unknown') + '.jpg'
    im.save(temp, "JPEG")


    if request.method == 'POST':

        form = ProjectRegistrationForm(request.POST)

        if form.is_valid():

            project_request = form.save()

            # Send email to Institute Delegate for approval
            send_project_request_email(project_request)

            os.remove('%s/img/captcha/project_%s.jpg' % (settings.MEDIA_ROOT, request.META.get('REMOTE_ADDR', 'unknown')))
            
            return HttpResponseRedirect(reverse('project_created', args=[project_request.id]))

    else:     
        form = ProjectRegistrationForm()

    imghash = sha.new(SALT+imgtext).hexdigest()

    return render_to_response('requests/project_request_form.html', { 'form': form, 'tempname': tempname, 'imghash': imghash }, context_instance=RequestContext(request))


def project_created(request, project_request_id):
    project_request = get_object_or_404(ProjectCreateRequest, pk=project_request_id)
    project = project_request.project
    person = project_request.project.leader
    
    log(person.user, project, 1, 'Requested project for approval')
    
    return render_to_response('requests/project_created.html', locals(), context_instance=RequestContext(request))


@login_required
def approve_project(request, project_request_id):
    project_request = get_object_or_404(ProjectCreateRequest, pk=project_request_id)
    project = project_request.project
    institute = project.institute
    leader = project.leader

    # Make sure the request is coming from the institutes' delegate
    if not request.user == institute.delegate.user:
        if not request.user == institute.active_delegate.user:
            return HttpResponseForbidden('<h1>Access Denied</h1>')
    
    project.is_approved = True
    project.is_active = True
    project.start_date = datetime.date.today()
    project.end_date = datetime.date.today() + datetime.timedelta(days=365)
    project.date_approved = datetime.date.today()
    project.approved_by = request.user.get_profile()
    project.save()

    log(request.user, project, 2, 'Approved Project')
    request.user.message_set.create(message="Project approved successfully and a notification email has been sent to %s" % leader)
    leader.user.message_set.create(message="Your project request has been accepted")

    if not leader.user.is_active:
        leader.activate()
        
    if project_request.needs_account:
        add_user_to_project(leader, project)
 
    send_project_approved_email(project_request)
    
    project_request.delete()

    return HttpResponseRedirect(reverse('kg_user_profile'))


@login_required
def reject_project(request, project_request_id):
    project_request = get_object_or_404(ProjectCreateRequest, pk=project_request_id)
    project = project_request.project
    institute = project.institute
    leader = project.leader
    user = leader.user

    # Make sure the request is coming from the institutes delegate
    if not request.user == institute.delegate.user:
        if not request.user == institute.active_delegate.user:
            return HttpResponseForbidden('<h1>Access Denied</h1>')

    send_project_rejected_email(project_request)

    log(request.user, project, 2, 'Rejected Project')
    request.user.message_set.create(message="Project rejected and a notification email has been sent to %s" % leader)
    
    project_request.delete()
    project.delete()
    if not leader.user.is_active:
        leader.delete()
        user.delete()

    return HttpResponseRedirect(reverse('kg_user_profile'))

    
@login_required
def request_detail(request, project_request_id):
    project_request = get_object_or_404(ProjectCreateRequest, pk=project_request_id)

    project = project_request.project
    person = project_request.project.leader

    # Make sure the request is coming from the institutes delegate
    if not request.user == project.institute.delegate.user:
        if not request.user == project.institute.active_delegate.user:
            return HttpResponseForbidden('<h1>Access Denied</h1>')

    
    return render_to_response('requests/project_request_detail.html', locals(), context_instance=RequestContext(request))

    

