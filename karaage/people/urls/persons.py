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
from django.urls import include, re_path

from karaage.people.views import persons


urlpatterns = [
    re_path(r"^$", persons.user_list, name="kg_person_list"),
    re_path(r"^struggling/$", persons.struggling, name="kg_person_struggling"),
    re_path(r"^locked/$", persons.locked_list, name="kg_person_locked"),
    re_path(r"^add/$", persons.add_user, name="kg_person_add"),
    re_path(
        r"^detail/(?P<username>%s)/" % settings.USERNAME_VALIDATION_RE, include("karaage.people.urls.person_detail")
    ),
]

urlpatterns += [
    re_path(
        r"^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/" r"(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$",
        persons.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    re_path(r"^reset/done/$", persons.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
