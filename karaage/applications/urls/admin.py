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

from karaage.applications.models import Application

urlpatterns = patterns('karaage.applications.views.admin',

    url(r'^$', 'application_list', name='kg_application_list'),
    url(r'^applicants/(?P<applicant_id>\d+)/$', 'applicant_edit', name='kg_applicant_edit'),
)

urlpatterns += patterns('karaage.admin.views',
    url(r'^(?P<object_id>\d+)/logs/$', 'log_detail', {'model': Application }, name='kg_application_logs'),
)

urlpatterns += patterns('karaage.applications.views.user',
    url(r'^invite/$', 'admin_send_invitation', name='kg_application_invite'),
    url(r'^invite/(?P<project_id>[-.\w]+)/$', 'admin_send_invitation', name='kg_application_invite'),

    url(r'^(?P<application_id>\d+)/$', 'application_detail_admin', name='kg_application_detail'),
    url(r'^(?P<application_id>\d+)/(?P<state>[-.\w]+)/$', 'application_detail_admin', name='kg_application_detail'),
    url(r'^(?P<application_id>\d+)/(?P<state>[-.\w]+)/(?P<label>[-.\w]+)/$', 'application_detail_admin', name='kg_application_detail'),
)

