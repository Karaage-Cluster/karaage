# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
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

from django.conf import settings
from django.conf.urls import url

from karaage.common.views import profile as common_profile
from karaage.people.views import profile as people_profile

profile_urlpatterns = [
    url(r'^$', common_profile.profile, name='kg_profile'),
    url(r'^logout/$', common_profile.logout, name='kg_profile_logout'),
]

profile_urlpatterns += [
    url(r'^personal/$',
        people_profile.profile_personal, name='kg_profile_personal'),
    url(r'^edit/$',
        people_profile.edit_profile, name='kg_profile_edit'),
    url(r'^password/$',
        people_profile.password_change, name='kg_profile_password'),
    url(r'^password_request/$',
        people_profile.password_request, name='kg_profile_reset'),
    url(r'^password_request/done/$',
        people_profile.password_request_done, name='kg_profile_reset_done'),
    url(r'^login/$', people_profile.login, name='kg_profile_login'),
    url(r'^login/(?P<username>%s)/$' % settings.USERNAME_VALIDATION_RE,
        people_profile.login, name="kg_profile_login"),
]

if settings.SHIB_SUPPORTED:
    profile_urlpatterns += [
        url(r'^saml/$',
            people_profile.saml_details, name='kg_profile_saml'),
        url(r'^slogin/$',
            people_profile.saml_login, name='kg_profile_login_saml'),
    ]
