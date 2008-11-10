from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import permission_required, login_required
from django.conf import settings
from django.contrib.sites.models import Site
import datetime

from karaage.people.models import Person
from karaage.projects.models import Project

from karaage.util.email_messages import send_bounced_warning
from karaage.people.forms import AdminPasswordChangeForm
from karaage.machines.forms import ShellForm
from karaage.util import get_date_range, log_object as log

@login_required
def delete_user(request, username):

    user = get_object_or_404(Person, user__username=username)

    if request.method == 'POST':
        user.deactivate()
        request.user.message_set.create(message="User '%s' was deleted succesfully" % user)
        return HttpResponseRedirect(user.get_absolute_url())
        
    return render_to_response('people/person_confirm_delete.html', locals(), context_instance=RequestContext(request))

delete_user = permission_required('main.delete_person')(delete_user)


@login_required
def user_detail(request, username):
    
    person = get_object_or_404(Person, user__username=username)

    if person.userrequest_set.count() > 0 and not person.user.is_active:
        requestor = True

    my_projects = person.project_set.all()
    my_pids = [ p.pid for p in my_projects ]
    
    not_project_list = Project.active.exclude(pid__in=my_pids)

    if request.REQUEST.has_key('showall'):
        showall = True

    #Add to project form
    if request.method == 'POST' and 'project-add' in request.POST:
        # Post means adding this user to a project
        data = request.POST.copy()
        project = Project.objects.get(pk=data['project'])
        if person.has_account(project.machine_category):
            project.users.add(person)
            request.user.message_set.create(message="User '%s' was added to %s succesfully" % (person, project))
            
            log(request.user, project, 2, '%s added to project' % person)
        else:
            no_account_error = "%s has no account on %s. Please create one first" % (person, project.machine_category)

    #change shell form
    shell_form = ShellForm()
    try:
        shell_form.initial = { 'shell': person.loginShell() }
    except:
        pass
    
    return render_to_response('people/person_detail.html', locals(), context_instance=RequestContext(request))


@login_required
def activate(request, username):

    user = get_object_or_404(Person, user__username=username)

    user.activate()

    request.user.message_set.create(message="User '%s' activated succesfully" % user)

    return HttpResponseRedirect('%spassword_change/' % user.get_absolute_url())
    
activate = permission_required('main.add_useraccount')(activate)


@login_required
def ldap_detail(request, username):
    person = get_object_or_404(Person, user__username=username)

    from placard.connection import LDAPConnection
    conn = LDAPConnection()
    try:
        ldap = conn.get_user('uid=%s' % username)
    except:
        raise Http404

    return render_to_response('people/ldap_detail.html', locals(), context_instance=RequestContext(request))


@login_required
def password_change(request, username):
    person = get_object_or_404(Person, user__username=username)
    
    if request.POST:
        form = AdminPasswordChangeForm(request.POST)
        
        if form.is_valid():
            form.save(person)
            request.user.message_set.create(message="Password changed successfully")
            log(request.user, person, 2, 'Changed password')
                        
            return HttpResponseRedirect(person.get_absolute_url())
    else:
        form = AdminPasswordChangeForm()
        
    return render_to_response('admin_password_change_form.html', locals(), context_instance=RequestContext(request))


@login_required
def lock_person(request, username):
    person = get_object_or_404(Person, user__username=username)

    person.lock()

    request.user.message_set.create(message="%s's account has been locked" % person)

    log(request.user, person, 2, 'Account locked')
    
    return HttpResponseRedirect(person.get_absolute_url())

@login_required
def unlock_person(request, username):
    person = get_object_or_404(Person, user__username=username)

    person.unlock()

    request.user.message_set.create(message="%s's account has been unlocked" % person)

    log(request.user, person, 2, 'Account unlocked')
    
    return HttpResponseRedirect(person.get_absolute_url())


@login_required
def bounced_email(request, username):
    person = get_object_or_404(Person, user__username=username)

    if request.method == 'POST':

        person.lock()
        send_bounced_warning(person)
        request.user.message_set.create(message="%s's account has been locked and emails have been sent" % person)
        log(request.user, person, 2, 'Emails sent to project leaders and account locked')
        return HttpResponseRedirect(person.get_absolute_url())

    return render_to_response('users/bounced_email.html', locals(), context_instance=RequestContext(request))

def user_job_list(request, username):
    today = datetime.date.today()
    start = today - datetime.timedelta(days=7)
    person = get_object_or_404(Person, user__username=username)
    start, end = get_date_range(request, start, today)

    job_list = []
    for ua in person.useraccount_set.all():
        job_list.extend(ua.cpujob_set.filter(date__range=(start, end)))


    return render_to_response('users/job_list.html', locals(), context_instance=RequestContext(request))

def user_comments(request, username):
    obj = get_object_or_404(Person, user__username=username)

    return render_to_response('comments/comments_list.html', locals(), context_instance=RequestContext(request))

def add_comment(request, username):
    obj = get_object_or_404(Person, user__username=username)

    return render_to_response('comments/add_comment.html', locals(), context_instance=RequestContext(request))
