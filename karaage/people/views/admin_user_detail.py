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
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages
import datetime

from karaage.people.models import Person
from karaage.projects.models import Project

from karaage.util.email_messages import send_bounced_warning
from karaage.people.forms import AdminPasswordChangeForm
from karaage.machines.forms import ShellForm
from karaage.util import get_date_range, log_object as log

@permission_required('people.delete_person')
def delete_user(request, username):

    user = get_object_or_404(Person, user__username=username)

    if request.method == 'POST':
        user.deactivate()
        messages.info(request, "User '%s' was deleted succesfully" % user)
        return HttpResponseRedirect(user.get_absolute_url())
        
    return render_to_response('people/person_confirm_delete.html', locals(), context_instance=RequestContext(request))


@login_required
def user_detail(request, username):
    
    person = get_object_or_404(Person, user__username=username)

    if person.projectjoinrequest_set.count() > 0 and not person.user.is_active:
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
        no_account_error = ''
        for mc in project.machine_categories.all():
            if not person.has_account(mc):
                no_account_error = "%s has no account on %s. Please create one first" % (person, project.machine_category)
                break
        if not no_account_error:
            project.users.add(person)
            messages.info(request, "User '%s' was added to %s succesfully" % (person, project))
            log(request.user, project, 2, '%s added to project' % person)

    #change shell form
    shell_form = ShellForm()
    try:
        shell_form.initial = { 'shell': person.loginShell() }
    except:
        pass
    
    return render_to_response('people/person_detail.html', locals(), context_instance=RequestContext(request))


@permission_required('machines.add_useraccount')
def activate(request, username):
    user = get_object_or_404(Person, user__username=username)
    user.activate()
    messages.info(request, "User '%s' activated succesfully" % user)

    return HttpResponseRedirect('%spassword_change/' % user.get_absolute_url())


@permission_required('people.change_person')
def password_change(request, username):
    person = get_object_or_404(Person, user__username=username)
    
    if request.POST:
        form = AdminPasswordChangeForm(request.POST)
        
        if form.is_valid():
            form.save(person)
            messages.info(request, "Password changed successfully")
            log(request.user, person, 2, 'Changed password')
            person.unlock()
            return HttpResponseRedirect(person.get_absolute_url())
    else:
        form = AdminPasswordChangeForm()
        
    return render_to_response('admin_password_change_form.html', locals(), context_instance=RequestContext(request))


@permission_required('people.change_person')
def lock_person(request, username):
    person = get_object_or_404(Person, user__username=username)
    person.lock()
    messages.info(request, "%s's account has been locked" % person)
    log(request.user, person, 2, 'Account locked')
    
    return HttpResponseRedirect(person.get_absolute_url())


@permission_required('people.change_person')
def unlock_person(request, username):
    person = get_object_or_404(Person, user__username=username)
    person.unlock()
    messages.info(request, "%s's account has been unlocked" % person)
    log(request.user, person, 2, 'Account unlocked')
    
    return HttpResponseRedirect(person.get_absolute_url())


@permission_required('people.change_person')
def bounced_email(request, username):
    person = get_object_or_404(Person, user__username=username)

    if request.method == 'POST':
        person.lock()
        send_bounced_warning(person)
        messages.info(request, "%s's account has been locked and emails have been sent" % person)
        log(request.user, person, 2, 'Emails sent to project leaders and account locked')
        for ua in person.useraccount_set.all():
            ua.change_shell(ua.previous_shell)
            ua.change_shell('/usr/local/sbin/bouncedemail')
        return HttpResponseRedirect(person.get_absolute_url())

    return render_to_response('people/bounced_email.html', locals(), context_instance=RequestContext(request))


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
    return render_to_response('comments/comments_list.html', {'obj': obj}, context_instance=RequestContext(request))


def add_comment(request, username):
    obj = get_object_or_404(Person, user__username=username)
    return render_to_response('comments/add_comment.html', {'obj': obj}, context_instance=RequestContext(request))
