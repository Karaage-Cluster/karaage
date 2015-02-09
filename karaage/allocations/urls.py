# Copyright 2014 The University of Melbourne
# Copyright 2015 VPAC
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
    'karaage.allocations.views',
    url(r'^project-(?P<project_id>\d+)/allocation-period/add/$',
        'allocation_period_add', name='allocation_period_add'),
    url(r'^project-(?P<project_id>\d+)/add-allocation/$',
        'add_edit_allocation', name='allocation_add'),
    url(r'^project-(?P<project_id>\d+)/edit-allocation/'
        '(?P<allocation_id>\d+)/$',
        'add_edit_allocation', name='allocation_edit'),
    url(r'^project-(?P<project_id>\d+)/delete-allocation/'
        '(?P<allocation_id>\d+)/$',
        'delete_allocation', name='allocation_delete'),
    url(r'^project-(?P<project_id>\d+)/add-grant/$',
        'add_edit_grant', name='grant_add'),
    url(r'^project-(?P<project_id>\d+)/edit-grant/(?P<grant_id>\d+)/$',
        'add_edit_grant', name='grant_edit'),
    url(r'^project-(?P<project_id>\d+)/delete-grant/(?P<grant_id>\d+)/$',
        'delete_grant', name='grant_delete'),
    url(r'^project-(?P<project_id>\d+)/add-scheme/$',
        'scheme_add', name='scheme_add'),
)
