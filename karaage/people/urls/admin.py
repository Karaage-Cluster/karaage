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
from karaage.people.models import Person


urlpatterns = patterns('karaage.people.views.admin',

    url(r'^$', 'user_list', name='kg_person_list'),
    url(r'^deleted/$', 'user_list', { 'queryset': Person.deleted.all(),}),
    url(r'^last_used/$', 'user_list', { 'queryset': Person.active.order_by('last_usage'),}),
    url(r'^no_project/$', 'user_list', { 'queryset': Person.active.filter(groups__project__isnull=True, account__isnull=False),}, name='kg_person_no_project'),
    url(r'^struggling/$', 'struggling', name='kg_person_struggling'),
    url(r'^no_default/$', 'no_default_list', name='kg_person_no_default'),
    url(r'^wrong_default/$', 'wrong_default_list', name='kg_person_wrong_default'),
    url(r'^no_account/$', 'no_account_list', name='kg_person_no_account'),
    url(r'^locked/$', 'locked_list', name='kg_person_locked'),

    url(r'^add/$', 'add_user', name='kg_person_add'),

    url(r'^accounts/(?P<account_id>\d+)/change_shell/$', 'change_account_shell', name='kg_account_shell'),
    url(r'^accounts/(?P<account_id>\d+)/edit/$', 'add_edit_account', name='kg_account_edit'),
    url(r'^accounts/(?P<account_id>\d+)/delete/$', 'delete_account', name='kg_account_delete'),
    url(r'^accounts/(?P<account_id>\d+)/makedefault/(?P<project_id>[-.\w]+)/$', 'make_default', name='kg_account_set_default'),

    (r'^(?P<username>%s)/' % settings.USERNAME_VALIDATION_RE, include('karaage.people.urls.admin_user_detail')),
)
