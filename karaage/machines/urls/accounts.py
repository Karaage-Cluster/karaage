# Copyright 2014-2015 VPAC
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

from django.conf.urls import patterns, url
from django.conf import settings

urlpatterns = patterns(
    'karaage.machines.views.accounts',
    url(r'^add/(?P<username>%s)/$' % settings.USERNAME_VALIDATION_RE,
        'add_account', name='kg_account_add'),
    url(r'^add_project/(?P<username>%s)/$' % settings.USERNAME_VALIDATION_RE,
        'add_project', name='kg_account_add_project'),
    url(r'^(?P<account_id>\d+)/$', 'account_detail',
        name='kg_account_detail'),
    url(r'^(?P<account_id>\d+)/edit/$', 'edit_account',
        name='kg_account_edit'),
    url(r'^(?P<account_id>\d+)/delete/$', 'delete_account',
        name='kg_account_delete'),
    url(r'^(?P<account_id>\d+)/makedefault/(?P<project_id>%s)/$'
        % settings.PROJECT_VALIDATION_RE,
        'make_default', name='kg_account_set_default'),

    url(r'^no_project/$', 'no_project_list',
        name='kg_account_no_project'),
    url(r'^no_default/$', 'no_default_list',
        name='kg_account_no_default'),
    url(r'^wrong_default/$', 'wrong_default_list',
        name='kg_account_wrong_default'),
    url(r'^no_account/$', 'no_account_list',
        name='kg_account_no_account'),
)
