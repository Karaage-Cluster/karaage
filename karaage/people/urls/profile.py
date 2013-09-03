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

urlpatterns = patterns('karaage.people.views.user',
    url(r'^slogin/$', 'saml_login', name='login_saml'),
    url(r'^saml/$', 'saml_details', name='saml_details'),
    url(r'^login/$', 'login', name='login'),
    url(r'^login/(?P<username>[-.\w]+)/$', 'login', name="login"),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^change_password/$', 'password_change', name='password_change'),
    url(r'^change_password/done/$', 'password_change_done', name='password_done'),
)
