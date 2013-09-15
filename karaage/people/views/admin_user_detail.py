# Copyright 2007-2013 VPAC
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
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.conf import settings

import datetime

from karaage.common.decorators import admin_required
from karaage.people.models import Person
from karaage.people.forms import AdminPasswordChangeForm, AddProjectForm
from karaage.people.emails import send_bounced_warning
from karaage.projects.models import Project
from karaage.projects.utils import add_user_to_project
from karaage.common import get_date_range, log_object as log
import karaage.common as util


@admin_required
def delete_user(request, username):

    person = get_object_or_404(Person, username=username)

    if request.method == 'POST':
        deleted_by = request.user
        person.deactivate(deleted_by)
        messages.success(request, "User '%s' was deleted succesfully" % person)
        return HttpResponseRedirect(person.get_absolute_url())
        
    return render_to_response('people/person_confirm_delete.html', locals(), context_instance=RequestContext(request))


@admin_required
def user_detail(request, username):
    
    person = get_object_or_404(Person, username=username)

    my_projects = person.projects.all()
    my_pids = [p.pid for p in my_projects]
    
    #Add to project form
    form = AddProjectForm(request.POST or None)
    if request.method == 'POST':
        # Post means adding this user to a project
        if form.is_valid():
            project = form.cleaned_data['project']
            add_user_to_project(person, project)
            messages.success(request, "User '%s' was added to %s succesfully" % (person, project))
            log(request.user, project, 2, '%s added to project' % person)

            return HttpResponseRedirect(person.get_absolute_url())

    return render_to_response('people/person_detail.html', locals(), context_instance=RequestContext(request))

@admin_required
def user_verbose(request, username):
    person = get_object_or_404(Person, username=username)

    from karaage.datastores import get_person_details
    person_details = get_person_details(person)

    from karaage.datastores import get_account_details
    account_details = []
    for ua in person.account_set.filter(date_deleted__isnull=True):
        details = get_account_details(ua)
        account_details.append(details)

    return render_to_response('people/person_verbose.html', locals(), context_instance=RequestContext(request))

@admin_required
def activate(request, username):
    person = get_object_or_404(Person, username=username, is_active=False)

    if request.method == 'POST':
        approved_by = request.user
        person.activate(approved_by)
        return HttpResponseRedirect(reverse('kg_person_password_change', args=[person.username]))
    
    return render_to_response('people/reactivate_confirm.html', {'person': person}, context_instance=RequestContext(request))


@admin_required
def password_change(request, username):
    person = get_object_or_404(Person, username=username)
    
    if request.POST:
        form = AdminPasswordChangeForm(request.POST)
        
        if form.is_valid():
            form.save(person)
            messages.success(request, "Password changed successfully")
            if person.is_locked():
                person.unlock()
            return HttpResponseRedirect(person.get_absolute_url())
    else:
        form = AdminPasswordChangeForm()
        
    return render_to_response('people/password_change_form.html', {'person': person, 'form': form}, context_instance=RequestContext(request))


@admin_required
def lock_person(request, username):
    person = get_object_or_404(Person, username=username)
    if request.method == 'POST':
        person.lock()
        messages.success(request, "%s's account has been locked" % person)
    return HttpResponseRedirect(person.get_absolute_url())


@admin_required
def unlock_person(request, username):
    person = get_object_or_404(Person, username=username)
    if request.method == 'POST':
        person.unlock()
        messages.success(request, "%s's account has been unlocked" % person)
    return HttpResponseRedirect(person.get_absolute_url())


@admin_required
def bounced_email(request, username):
    person = get_object_or_404(Person, username=username)
    if request.method == 'POST':
        person.lock()
        send_bounced_warning(person)
        messages.success(request, "%s's account has been locked and emails have been sent" % person)
        log(request.user, person, 2, 'Emails sent to project leaders and account locked')
        for ua in person.account_set.all():
            ua.change_shell(ua.previous_shell)
            ua.change_shell(settings.BOUNCED_SHELL)
        return HttpResponseRedirect(person.get_absolute_url())

    return render_to_response('people/bounced_email.html', locals(), context_instance=RequestContext(request))


@admin_required
def user_job_list(request, username):
    today = datetime.date.today()
    start = today - datetime.timedelta(days=7)
    person = get_object_or_404(Person, username=username)
    start, end = get_date_range(request, start, today)

    job_list = []
    for ua in person.account_set.all():
        job_list.extend(ua.cpujob_set.filter(date__range=(start, end)))

    return render_to_response('users/job_list.html', locals(), context_instance=RequestContext(request))


@admin_required
def add_comment(request, username):
    obj = get_object_or_404(Person, username=username)
    return util.add_comment(request, "People", reverse("kg_person_list"), unicode(obj), obj)
