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


urlpatterns = patterns('karaage.people.views.user',

    url(r'^(?P<username>[-.\w]+)/$', 'user_detail', name='kg_user_detail'),
    url(r'^(?P<username>[-.\w]+)/flag_left/$', 'flag_left'),
    url(r'^(?P<username>[-.\w]+)/login/$', 'login'),
    url(r'^accounts/(?P<useraccount_id>\d+)/makedefault/(?P<project_id>[-.\w]+)/$', 'make_default', name='kg_user_make_default'),
)
