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

urlpatterns = patterns('karaage.applications.views.admin',

    url(r'^$', 'application_list', name='kg_account_request_list'),
    url(r'^add/$', 'add_edit_userapplication', name='kg_userapplication_add'),
    url(r'^(?P<application_id>\d+)/$', 'userapplication_detail', name='kg_userapplication_detail'),
    url(r'^(?P<application_id>\d+)/edit/$', 'add_edit_userapplication', name='kg_userapplication_edit'),
    url(r'^(?P<application_id>\d+)/approve/$', 'approve_userapplication', name='kg_userapplication_approve'),
    url(r'^(?P<application_id>\d+)/decline/$', 'decline_userapplication', name='kg_userapplication_decline'),
    url(r'^(?P<application_id>\d+)/complete/$', 'userapplication_complete', name='kg_userapplication_complete'),

)

