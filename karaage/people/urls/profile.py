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

from django.conf.urls import *
from django.conf import settings

from karaage.common import get_hooks

urlpatterns = patterns('karaage.people.views.profile',
    url(r'^$', 'profile', name='kg_profile'),
    url(r'^personal/$', 'profile_personal', name='kg_profile_personal'),
    url(r'^accounts/$', 'profile_accounts', name='kg_profile_accounts'),
    url(r'^software/$', 'profile_software', name='kg_profile_software'),
    url(r'^projects/$', 'profile_projects', name='kg_profile_projects'),
    url(r'^institutes/$', 'profile_institutes', name='kg_profile_institutes'),
    url(r'^edit/$', 'edit_profile', name='kg_profile_edit'),

    url(r'^slogin/$', 'saml_login', name='kg_profile_login_saml'),
    url(r'^saml/$', 'saml_details', name='kg_profile_saml'),
    url(r'^login/$', 'login', name='kg_profile_login'),
    url(r'^login/(?P<username>%s)/$' % settings.USERNAME_VALIDATION_RE, 'login', name="kg_profile_login"),
    url(r'^logout/$', 'logout', name='kg_profile_logout'),

    url(r'^password/$', 'password_change', name='kg_profile_password'),
    url(r'^password_request/$', 'password_request', name='kg_profile_reset'),
    url(r'^password_request/done/$', 'password_request_done', name='kg_profile_reset_done'),
)

for hook in get_hooks("profile_urlpatterns"):
    urlpatterns += hook
    del hook
