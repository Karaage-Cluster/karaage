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

from django.conf.urls import *


urlpatterns = patterns('karaage.applications.views.user',

    url(r'^pending/$', 'pending_applications', name='kg_application_pendinglist'),

    url(r'^new/$', 'new_application', name='kg_application_new'),

    url(r'^invite/(?P<project_id>[-.\w]+)/$', 'send_invitation', name='kg_application_invite'),

    url(r'^(?P<application_id>\d+)/$', 'application_detail', name='kg_application_detail'),
    url(r'^(?P<application_id>\d+)/(?P<state>[-.\w]+)/$', 'application_detail', name='kg_application_detail'),
    url(r'^(?P<application_id>\d+)/(?P<state>[-.\w]+)/(?P<label>[-.\w]+)/$', 'application_detail', name='kg_application_detail'),

    url(r'^(?P<token>[-.\w]+)/$', 'application_unauthenticated', name='kg_application_unauthenticated'),
    url(r'^(?P<token>[-.\w]+)/(?P<state>[-.\w]+)/$', 'application_unauthenticated', name='kg_application_unauthenticated'),
    url(r'^(?P<token>[-.\w]+)/(?P<state>[-.\w]+)/(?P<label>[-.\w]+)/$', 'application_unauthenticated', name='kg_application_unauthenticated'),
)
