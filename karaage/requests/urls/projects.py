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

from django.conf.urls.defaults import *


urlpatterns = patterns('karaage.requests.views.projects',           
    url(r'^$', 'project_registration', name='project_registration'),
    url(r'^created/(?P<project_request_id>\d+)/$', 'project_created', name='project_created'),
    url(r'^approve/(?P<project_request_id>\d+)/$', 'approve_project', name='user_approve_project'),
    url(r'^reject/(?P<project_request_id>\d+)/$', 'reject_project', name='user_reject_project'),

    url(r'^(?P<project_request_id>\d+)/$', 'request_detail', name='user_project_request_detail'),
    
)
