# Copyright 2007-2014 VPAC
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

from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^persons/', include('karaage.people.urls.persons')),
    url(r'^groups/', include('karaage.people.urls.groups')),
)

profile_urlpatterns = patterns('karaage.people.views.persons',
    url(r'^personal/$', 'profile_personal', name='kg_profile_personal'),
    url(r'^edit/$', 'edit_profile', name='kg_profile_edit'),
    url(r'^password/$', 'password_change', name='kg_profile_password'),
    url(r'^password_request/$', 'password_request', name='kg_profile_reset'),
    url(r'^password_request/done/$', 'password_request_done', name='kg_profile_reset_done'),
)
