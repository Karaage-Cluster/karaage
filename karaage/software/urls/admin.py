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

from karaage.software.models import Software

urlpatterns = patterns('karaage.software.views.admin',
    url(r'^$', 'software_list', name='kg_software_list'),
    url(r'^add/$', 'add_package', name='kg_software_add'),

    url(r'^categories/$', 'category_list', name='kg_software_category_list'),
    url(r'^categories/add/$', 'category_create', name='kg_software_category_create'),
    url(r'^categories/(?P<category_id>\d+)/edit/$', 'category_edit', name='kg_software_category_edit'),

    url(r'^requests/$', 'softwarerequest_list', name='kg_software_request_list'),
    url(r'^requests/(?P<softwarerequest_id>\d+)/approve/$', 'softwarerequest_approve', name='kg_software_request_approve'),
    url(r'^requests/(?P<softwarerequest_id>\d+)/decline/$', 'softwarerequest_delete', name='kg_software_request_delete'),

    url(r'^(?P<software_id>\d+)/$', 'software_detail', name='kg_software_detail'),
    url(r'^(?P<software_id>\d+)/edit/$', 'software_edit', name='kg_software_edit'),
    url(r'^(?P<software_id>\d+)/delete/$', 'software_delete', name='kg_software_delete'),
    url(r'^(?P<software_id>\d+)/verbose/$', 'software_verbose', name='kg_software_verbose'),
    url(r'^(?P<software_id>\d+)/stats/$', 'software_stats', name='kg_software_stats'),
    url(r'^(?P<software_id>\d+)/remove/(?P<user_id>\d+)/$', 'remove_member', name='kg_software_removeuser'),
    url(r'^(?P<software_id>\d+)/license/add/$', 'add_edit_license', name='kg_software_license_add'),
    url(r'^(?P<software_id>\d+)/license/edit/(?P<license_id>\d+)/$', 'add_edit_license', name='kg_software_license_edit'),
    url(r'^(?P<software_id>\d+)/version/add/$', 'add_edit_version', name='kg_software_version_add'),
    url(r'^(?P<software_id>\d+)/version/edit/(?P<version_id>\d+)/$', 'add_edit_version', name='kg_software_version_edit'),
    url(r'^(?P<software_id>\d+)/version/stats/(?P<version_id>\d+)/$', 'version_stats', name='kg_software_version_stats'),
    url(r'^(?P<software_id>\d+)/version/delete/(?P<version_id>\d+)/$', 'delete_version', name='kg_software_version_delete'),
    url(r'^(?P<software_id>\d+)/logs/$', 'software_logs', name='kg_software_logs'),
    url(r'^(?P<software_id>\d+)/add_comment/$', 'add_comment', name='kg_software_add_comment'),

    url(r'^license/(?P<license_id>\d+)/$', 'license_detail', name='kg_software_license_detail'),
    url(r'^license/(?P<license_id>\d+)/delete/$', 'license_delete', name='kg_software_license_delete'),
)

urlpatterns += patterns('karaage.admin.views',
)
