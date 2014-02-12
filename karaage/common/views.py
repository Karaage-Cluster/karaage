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

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

from karaage.common import is_admin
from karaage.common.decorators import admin_required
from karaage.people.models import Person
from karaage.projects.models import Project


@admin_required
def admin_index(request):
    var = {
        'newest_users': Person.objects.order_by('-date_approved', '-id').filter(date_approved__isnull=False).select_related()[:5],
        'newest_projects': Project.objects.order_by('-date_approved').filter(date_approved__isnull=False).filter(is_active=True).select_related()[:5],
        'recent_actions': request.user.logentry_set.all()[:10],
    }
    return render_to_response('index.html', var, context_instance=RequestContext(request))

def index(request):
    if settings.ADMIN_REQUIRED or is_admin(request):
        return admin_index(request)
    return render_to_response('index.html', context_instance=RequestContext(request))
