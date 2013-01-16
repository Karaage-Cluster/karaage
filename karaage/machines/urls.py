# Copyright 2007-2010 VPAC
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
from django.contrib.auth.decorators import permission_required
from django.views.generic.create_update import update_object, create_object
from models import Machine, MachineCategory


urlpatterns = patterns('django.views.generic.create_update',
    url(r'^add/$', permission_required('machines.add_machine')(create_object), {'model': Machine}),
    url(r'^(?P<object_id>\d+)/edit/$', permission_required('machines.change_machine')(update_object), {'model': Machine}),
    url(r'^categories/add/$', permission_required('machines.add_machinecategory')(create_object), {'model': MachineCategory}, name='kg_machinecategory_add'),
    url(r'^categories/(?P<object_id>\d+)/edit/$', permission_required('machines.change_machinecategory')(update_object), {'model': MachineCategory}, name='kg_machinecategory_edit'),
)

urlpatterns += patterns('karaage.machines.views',

    url(r'^$', 'index', name='kg_machine_list'),
    url(r'^(?P<machine_id>\d+)/$', 'machine_detail', name='kg_machine_detail'),
    url(r'^(?P<machine_id>\d+)/user_accounts/$', 'machine_accounts'),
    url(r'^(?P<machine_id>\d+)/projects/$', 'machine_projects'),
)
