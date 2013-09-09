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
from django.core.urlresolvers import get_script_prefix

urlpatterns = patterns('karaage.legacy.simple',           
    url(r'^$', 'redirect_to', {'url': '%sapplications/new-project/' % get_script_prefix()}, name='project_registration'),
    url(r'^approve/(?P<project_request_id>\d+)/$', 'redirect_to', {'url': '%sapplications/pending/' % get_script_prefix()}, name='user_approve_project'),
    url(r'^reject/(?P<project_request_id>\d+)/$', 'redirect_to', {'url': '%sapplications/pending/' % get_script_prefix()}, name='user_reject_project'),
    url(r'^(?P<project_request_id>\d+)/$', 'redirect_to', {'url': '%sapplications/pending/' % get_script_prefix()}, name='user_project_request_detail'),
    
)
