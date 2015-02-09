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

from django.conf.urls import patterns, url
from django.conf import settings

urlpatterns = patterns(
    'karaage.people.views.groups',
    url(r'^$', 'group_detail', name='kg_group_detail'),
    url(r'^verbose/$', 'group_verbose', name='kg_group_verbose'),
    url(r'^delete/$', 'delete_group', name='kg_group_delete'),
    url(r'^add/$', 'add_group_member', name='kg_group_add_person'),
    url(r'^remove/(?P<username>%s)/$' % settings.USERNAME_VALIDATION_RE,
        'remove_group_member', name='kg_group_remove_person'),
    url(r'^logs/$', 'group_logs', name='kg_group_logs'),
    url(r'^add_comment/$', 'add_comment', name='kg_group_add_comment'),
    url(r'^edit/$', 'edit_group', name='kg_group_edit'),
)
