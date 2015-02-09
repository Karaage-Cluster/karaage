# Copyright 2013-2015 VPAC
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

from django.conf.urls import patterns, url, include
from django.conf import settings


urlpatterns = patterns(
    'karaage.people.views.groups',
    url(r'^$', 'group_list', name='kg_group_list'),
    url(r'^add/$', 'add_group', name='kg_group_add'),
    (r'^detail/(?P<group_name>%s)/' % settings.GROUP_VALIDATION_RE,
        include('karaage.people.urls.group_detail')),
)
