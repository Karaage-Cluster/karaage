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
from django.conf import settings


urlpatterns = patterns('karaage.people.views.user',
    url(r'^detail/(?P<username>%s)/$' % settings.USERNAME_VALIDATION_RE, 'user_detail', name='kg_person_detail'),
    url(r'^request_password/$', 'password_reset_request', name='password_reset_request'),
    url(r'^accounts/(?P<account_id>\d+)/change_shell/$', 'change_account_shell', name='kg_account_shell'),
    url(r'^accounts/(?P<account_id>\d+)/makedefault/(?P<project_id>[-.\w]+)/$', 'make_default', name='kg_account_set_default'),
)

from karaage.people.forms import SetPasswordForm
urlpatterns += patterns('django.contrib.auth.views',
    url(r'^password_reset/done/$', 'password_reset_done', name='password_reset_done'),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm', {'set_password_form': SetPasswordForm}, name='password_reset_confirm'),
    url(r'^reset/done/$', 'password_reset_complete', name='password_reset_complete'),
)
