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

from karaage.people.models import Person, Group
from karaage.people.forms import AddGroupMemberForm


@permission_required('people.delete_group')
def delete_group(request, group_name):

    group = get_object_or_404(Group, name=group_name)

    if request.method == 'POST':
        group.delete()
        messages.success(request, "Group '%s' was deleted succesfully" % group)
        return HttpResponseRedirect(group.get_absolute_url())

    return render_to_response('people/group_confirm_delete.html', locals(), context_instance=RequestContext(request))


@login_required
def group_detail(request, group_name):
    group = get_object_or_404(Group, name=group_name)

    if request.user.has_perm('people.change_person'):
        form = AddGroupMemberForm(instance=group)

    return render_to_response('people/group_detail.html', locals(), context_instance=RequestContext(request))


@login_required
def group_verbose(request, group_name):
    group = get_object_or_404(Group, name=group_name)

    from karaage.datastores import get_group_details
    group_details = get_group_details(group)

    return render_to_response('people/group_verbose.html', locals(), context_instance=RequestContext(request))


@login_required
def add_group_member(request, group_name):
    if not request.user.has_perm('people.change_person'):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    group = get_object_or_404(Group, name=group_name)
    if request.method == 'POST':
        form = AddGroupMemberForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(group.get_absolute_url())
    else:
        form = AddGroupMemberForm(instance=group)

    return render_to_response('people/group_add_member.html', locals(), context_instance=RequestContext(request))


@login_required
def remove_group_member(request, group_name, username):
    if not request.user.has_perm('people.change_person'):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    group = get_object_or_404(Group, name=group_name)
    person = get_object_or_404(Person, user__username=username)
    if request.method == 'POST':
        group.remove_person(person)
        return HttpResponseRedirect(group.get_absolute_url())

    return render_to_response('people/group_remove_member.html', locals(), context_instance=RequestContext(request))
