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

urlpatterns = patterns('karaage.common.views.profile',
    url(r'^$', 'profile', name='kg_profile'),

    url(r'^slogin/$', 'saml_login', name='kg_profile_login_saml'),
    url(r'^saml/$', 'saml_details', name='kg_profile_saml'),
    url(r'^login/$', 'login', name='kg_profile_login'),
    url(r'^login/(?P<username>%s)/$' % settings.USERNAME_VALIDATION_RE, 'login', name="kg_profile_login"),
    url(r'^logout/$', 'logout', name='kg_profile_logout'),
)

for hook in get_hooks("profile_urlpatterns"):
    urlpatterns += hook
    del hook
