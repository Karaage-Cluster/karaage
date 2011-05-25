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

from django.conf import settings

from karaage.applications.models import Application

def common(request):
    ctx = {}
    ctx['GRAPH_URL'] = settings.GRAPH_URL
    ctx['org_name'] = settings.ACCOUNTS_ORG_NAME
    ctx['accounts_email'] = settings.ACCOUNTS_EMAIL
    return ctx


def registration(request):
    ctx = {}
    if request.user.is_authenticated():
        user_apps = request.user.get_profile().leaders.filter(userapplication__state=Application.WAITING_FOR_LEADER)
        project_apps = request.user.get_profile().delegate.filter(projectapplication__state=Application.WAITING_FOR_DELEGATE)
        if user_apps or project_apps:
            ctx['pending_applications'] = True
    return ctx


def admin(request):
    ctx = {}
    ctx['pending_apps'] = Application.objects.filter(state=Application.WAITING_FOR_ADMIN)
    return ctx
