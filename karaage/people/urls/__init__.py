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
from django.urls import re_path

from karaage.common.views import profile as common_profile
from karaage.people.views import profile as people_profile


profile_urlpatterns = [
    re_path(r"^$", common_profile.profile, name="kg_profile"),
    re_path(r"^logout/$", common_profile.logout, name="kg_profile_logout"),
]

profile_urlpatterns += [
    re_path(r"^personal/$", people_profile.profile_personal, name="kg_profile_personal"),
    re_path(r"^edit/$", people_profile.edit_profile, name="kg_profile_edit"),
    re_path(r"^password/$", people_profile.password_change, name="kg_profile_password"),
    re_path(r"^password_request/$", people_profile.password_request, name="kg_profile_reset"),
    re_path(r"^password_request/done/$", people_profile.password_request_done, name="kg_profile_reset_done"),
    re_path(r"^login/$", people_profile.login, name="kg_profile_login"),
    re_path(
        r"^login/(?P<username>%s)/$" % settings.USERNAME_VALIDATION_RE, people_profile.login, name="kg_profile_login"
    ),
]

if settings.AAF_RAPID_CONNECT_ENABLED:
    profile_urlpatterns += [
        re_path(
            r"^arc/$",
            people_profile.profile_aaf_rapid_connect,
            name="kg_profile_arc",
        ),
        re_path(
            r"^slogin/$",
            people_profile.aaf_rapid_connect_login,
            name="kg_profile_login_arc",
        ),
    ]
