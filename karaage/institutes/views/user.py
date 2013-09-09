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
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from karaage.institutes.models import Institute


@login_required
def institute_users_list(request, institute_id):

    institute = get_object_or_404(Institute, pk=institute_id)

    if not request.user in institute.delegates.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    user_list = institute.person_set.select_related()

    return render_to_response('institutes/institute_user_list.html', locals(), context_instance=RequestContext(request))


@login_required
def institute_projects_list(request, institute_id):

    institute = get_object_or_404(Institute, pk=institute_id)

    if not request.user in institute.delegates.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    project_list = institute.project_set.select_related()

    return render_to_response('institutes/institute_projects_list.html', locals(), context_instance=RequestContext(request))
