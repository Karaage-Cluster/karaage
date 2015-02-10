# Copyright 2008, 2010, 2014-2015 VPAC
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

urlpatterns = patterns(
    'karaage.machines.views.machines',
    url(r'^$', 'category_list', name='kg_machine_category_list'),
    url(r'^add/$', 'machine_create', name='kg_machine_add'),
    url(r'^(?P<machine_id>\d+)/$', 'machine_detail', name='kg_machine_detail'),
    url(r'^(?P<machine_id>\d+)/edit/$', 'machine_edit',
        name='kg_machine_edit'),
    url(r'^(?P<machine_id>\d+)/password/$', 'machine_password',
        name='kg_machine_password'),
    url(r'^(?P<machine_id>\d+)/logs/$', 'machine_logs',
        name='kg_machine_logs'),
    url(r'^(?P<machine_id>\d+)/add_comment/$', 'machine_add_comment',
        name='kg_machine_add_comment'),
    url(r'^categories/add/$', 'category_create',
        name='kg_machine_category_add'),
    url(r'^categories/(?P<category_id>\d+)/$', 'category_detail',
        name='kg_machine_category_detail'),
    url(r'^categories/(?P<category_id>\d+)/accounts/$', 'category_accounts',
        name='kg_machine_category_accounts'),
    url(r'^categories/(?P<category_id>\d+)/projects/$', 'category_projects',
        name='kg_machine_category_projects'),
    url(r'^categories/(?P<category_id>\d+)/edit/$', 'category_edit',
        name='kg_machine_category_edit'),
    url(r'^categories/(?P<category_id>\d+)/logs/$', 'category_logs',
        name='kg_machine_category_logs'),
    url(r'^categories/(?P<category_id>\d+)/add_comment/$',
        'category_add_comment',
        name='kg_machine_category_add_comment'),
)
