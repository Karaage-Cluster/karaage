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

from django.conf.urls import url

from karaage.machines.views import machines

urlpatterns = [
    url(r'^$', machines.category_list, name='kg_machine_category_list'),
    url(r'^add/$', machines.machine_create, name='kg_machine_add'),
    url(r'^(?P<machine_id>\d+)/$',
        machines.machine_detail, name='kg_machine_detail'),
    url(r'^(?P<machine_id>\d+)/edit/$', machines.machine_edit,
        name='kg_machine_edit'),
    url(r'^(?P<machine_id>\d+)/password/$', machines.machine_password,
        name='kg_machine_password'),
    url(r'^(?P<machine_id>\d+)/logs/$', machines.machine_logs,
        name='kg_machine_logs'),
    url(r'^(?P<machine_id>\d+)/add_comment/$', machines.machine_add_comment,
        name='kg_machine_add_comment'),
    url(r'^categories/add/$', machines.category_create,
        name='kg_machine_category_add'),
    url(r'^categories/(?P<category_id>\d+)/$', machines.category_detail,
        name='kg_machine_category_detail'),
    url(r'^categories/(?P<category_id>\d+)/accounts/$',
        machines.category_accounts, name='kg_machine_category_accounts'),
    url(r'^categories/(?P<category_id>\d+)/projects/$',
        machines.category_projects, name='kg_machine_category_projects'),
    url(r'^categories/(?P<category_id>\d+)/edit/$', machines.category_edit,
        name='kg_machine_category_edit'),
    url(r'^categories/(?P<category_id>\d+)/logs/$', machines.category_logs,
        name='kg_machine_category_logs'),
    url(r'^categories/(?P<category_id>\d+)/add_comment/$',
        machines.category_add_comment,
        name='kg_machine_category_add_comment'),
]
