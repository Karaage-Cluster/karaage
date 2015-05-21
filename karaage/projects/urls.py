# Copyright 2008, 2010, 2013-2015 VPAC
# Copyright 2014 The University of Melbourne
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
    'karaage.projects.views',
    url(r'^$', 'project_list', name='kg_project_list'),
    url(r'^add/$', 'add_edit_project', name='kg_project_add'),
    url(r'^no_users/$', 'no_users', name='kg_empty_projects_list'),

    url(r'^quota/(?P<projectquota_id>\d+)/$',
        'projectquota_edit', name='kg_projectquota_edit'),
    url(r'^quota/(?P<projectquota_id>\d+)/delete/$',
        'projectquota_delete', name='kg_projectquota_delete'),

    url(r'^(?P<project_id>\d+)/$',
        'project_detail', name='kg_project_detail'),
    url(r'^(?P<project_id>\d+)/verbose/$',
        'project_verbose', name='kg_project_verbose'),
    url(r'^(?P<project_id>\d+)/edit/$',
        'add_edit_project', name='kg_project_edit'),
    url(r'^(?P<project_id>\d+)/undelete/$',
        'undelete_project', name='kg_project_undelete'),
    url(r'^(?P<project_id>\d+)/delete/$',
        'delete_project', name='kg_project_delete'),
    url(r'^(?P<project_id>\d+)/remove_user/(?P<username>%s)/$'
        % (settings.USERNAME_VALIDATION_RE,),
        'remove_user', name='kg_remove_project_member'),
    url(r'^(?P<project_id>\d+)/grant/(?P<username>%s)/$'
        % (settings.USERNAME_VALIDATION_RE,),
        'grant_leader', name='kg_grant_leader'),
    url(r'^(?P<project_id>\d+)/revoke/(?P<username>%s)/$'
        % (settings.USERNAME_VALIDATION_RE,),
        'revoke_leader', name='kg_revoke_leader'),
    url(r'^(?P<project_id>\d+)/logs/$',
        'project_logs', name='kg_project_logs'),
    url(r'^(?P<project_id>\d+)/add_comment/$',
        'add_comment', name='kg_project_add_comment'),
    url(r'^(?P<project_id>\d+)/quota/add/$',
        'projectquota_add', name='kg_projectquota_add'),
)

profile_urlpatterns = patterns(
    'karaage.projects.views',
    url(r'^projects/$', 'profile_projects', name='kg_profile_projects'),
)
