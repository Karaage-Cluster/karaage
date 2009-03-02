from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required, login_required

from karaage.requests.models import ProjectJoinRequest
from karaage.util import log_object as log
from karaage.datastores import create_account
from karaage.util.email_messages import *

@login_required
def account_request_list(request):

    request_list = ProjectJoinRequest.objects.filter(leader_approved=True)
    
    return render_to_response('requests/user_request_list.html', locals(), context_instance=RequestContext(request)) 

account_request_list = permission_required('machines.add_useraccount')(account_request_list)


def account_request_detail(request, ar_id):
    ar = get_object_or_404(ProjectJoinRequest, pk=ar_id)

    person = ar.person
    project = ar.project

    return render_to_response('requests/user_request_detail.html', locals(), context_instance=RequestContext(request))

account_request_detail = permission_required('machines.add_useraccount')(account_request_detail)


def account_request_approve(request, ar_id):
    join_request = get_object_or_404(ProjectJoinRequest, pk=ar_id)

    person = join_request.person
    project = join_request.project

    project.users.add(person)

    person.activate()

    log(request.user, person, 2, 'Added to project %s' % project)
    log(request.user, project, 2, '%s added to project' % person)

    # Create accounts on all the MachineCategories attached to the project
    for mc in project.machine_categories.all():
        if not person.has_account(mc):
            create_account(person, project, mc)

    send_account_approved_email(join_request)
    join_request.delete()

    request.user.message_set.create(message="User '%s' approved succesfully and an email has been sent" % person)
    return HttpResponseRedirect(person.get_absolute_url())

account_request_approve = permission_required('machines.add_useraccount')(account_request_approve)



def account_request_reject(request, ar_id):
    ar = get_object_or_404(ProjectJoinRequest, pk=ar_id)

    person = ar.person
    user = person.user
    project = ar.project

    send_account_rejected_email(ar)
    
    ar.delete()

    log(request.user, person, 2, "Account rejected")

    if not person.is_active:
        person.delete()
        user.delete()

    request.user.message_set.create(message="User '%s' rejected succesfully and an email has been sent" % person)
        
    return HttpResponseRedirect(reverse('kg_account_request_list'))

account_request_reject = permission_required('machines.add_useraccount')(account_request_reject)
    
