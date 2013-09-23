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

from django.conf.urls import *


urlpatterns = patterns('karaage.applications.views',

    url(r'^$', 'user.pending_applications', name='kg_application_list'),

    url(r'^project/new/$', 'project.new_application', name='kg_application_new'),
    url(r'^project/invite/(?P<project_id>[-.\w]+)/$', 'project.send_invitation', name='kg_application_invite'),

    url(r'^software/new/(?P<software_license_id>\d+)/$', 'software.new_application', name='kg_application_software_new'),

    url(r'^(?P<application_id>\d+)/$', 'user.application_detail', name='kg_application_detail'),
    url(r'^(?P<application_id>\d+)/(?P<state>[-.\w]+)/$', 'user.application_detail', name='kg_application_detail'),
    url(r'^(?P<application_id>\d+)/(?P<state>[-.\w]+)/(?P<label>[-.\w]+)/$', 'user.application_detail', name='kg_application_detail'),

    url(r'^(?P<token>[-.\w]+)/$', 'user.application_unauthenticated', name='kg_application_unauthenticated'),
    url(r'^(?P<token>[-.\w]+)/(?P<state>[-.\w]+)/$', 'user.application_unauthenticated', name='kg_application_unauthenticated'),
    url(r'^(?P<token>[-.\w]+)/(?P<state>[-.\w]+)/(?P<label>[-.\w]+)/$', 'user.application_unauthenticated', name='kg_application_unauthenticated'),
)
