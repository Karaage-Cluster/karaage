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

from karaage.projects.models import Project

urlpatterns = patterns('karaage.projects.views.admin',
    url(r'^$', 'project_list', name='kg_project_list'),
    url(r'^add/$', 'add_edit_project', name='kg_add_project'),
    url(r'^no_users/$', 'no_users', name='kg_empty_projects_list'),
    url(r'^over_quota/$', 'over_quota', name='kg_projects_over_quota'),
    url(r'^by_last_usage/$', 'project_list', {'queryset': Project.active.order_by('last_usage')}, name='kg_project_last_usage_list'),
    url(r'^custom_cap/$', 'project_list', {'queryset': Project.active.filter(projectquota__cap__isnull=False)}, name='kg_project_custom_cap_list'),
    url(r'^projects_by_cap_used/$', 'projects_by_cap_used', name='kg_projects_by_cap_used'),

    url(r'^quota/(?P<projectquota_id>\d+)/$', 'projectquota_edit', name='kg_projectquota_edit'),
    url(r'^quota/(?P<projectquota_id>\d+)/delete/$', 'projectquota_delete', name='kg_projectquota_delete'),

    url(r'^(?P<project_id>[-.\w]+)/$', 'project_detail', name='kg_project_detail'),
    url(r'^(?P<project_id>[-.\w]+)/verbose/$', 'project_verbose', name='kg_project_verbose'),
    url(r'^(?P<project_id>[-.\w]+)/edit/$', 'add_edit_project', name='kg_edit_project'),
    url(r'^(?P<project_id>[-.\w]+)/delete/$', 'delete_project', name='kg_delete_project'),
    url(r'^(?P<project_id>[-.\w]+)/remove_user/(?P<username>%s)/$' % settings.USERNAME_VALIDATION_RE, 'remove_user', name='kg_remove_project_member'),
    url(r'^(?P<project_id>[-.\w]+)/logs/$', 'project_logs', name='kg_project_logs'),
    url(r'^(?P<project_id>[-.\w]+)/add_comment/$', 'add_comment', name='kg_project_add_comment'),
    url(r'^(?P<project_id>[-.\w]+)/quota/add/$', 'projectquota_add', name='kg_projectquota_add'),
)
