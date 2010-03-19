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


urlpatterns = patterns('karaage.requests.views.user',

    url(r'^$', 'user_registration', name='user_registration'),
    url(r'^cancel/(?P<user_request_id>\d+)/$', 'cancel_user_registration'),
    url(r'^choose_project/$', 'choose_project', name='user_choose_project'),
    url(r'^(?P<user_request_id>\d+)/created/$', 'account_created', name='kg_user_account_pending'),
                        
    url(r'^(?P<user_request_id>\d+)/$', 'request_detail', name='user_account_request_detail'),
    url(r'^(?P<user_request_id>\d+)/approve/$', 'approve_person', name='user_approve_account'),
    url(r'^(?P<user_request_id>\d+)/reject/$', 'reject_person', name='user_reject_account'),

                       
)

