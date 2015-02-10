# Copyright 2008, 2010-2011, 2013-2015 VPAC
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
    'karaage.institutes.views',
    url(r'^$', 'institute_list', name='kg_institute_list'),
    url(r'^add/$', 'add_edit_institute', name='kg_institute_add'),

    url(r'^quota/(?P<institutequota_id>\d+)/$',
        'institutequota_edit', name='kg_institutequota_edit'),
    url(r'^quota/(?P<institutequota_id>\d+)/delete/$',
        'institutequota_delete', name='kg_institutequota_delete'),

    url(r'^(?P<institute_id>\d+)/$',
        'institute_detail', name='kg_institute_detail'),
    url(r'^(?P<institute_id>\d+)/verbose/$',
        'institute_verbose', name='kg_institute_verbose'),
    url(r'^(?P<institute_id>\d+)/edit/$',
        'add_edit_institute', name='kg_institute_edit'),
    url(r'^(?P<institute_id>\d+)/quota/add/$',
        'institutequota_add', name='kg_institutequota_add'),
    url(r'^(?P<institute_id>[-.\w]+)/logs/$',
        'institute_logs', name='kg_institute_logs'),
    url(r'^(?P<institute_id>[-.\w]+)/add_comment/$',
        'add_comment', name='kg_institute_add_comment'),

)

profile_urlpatterns = patterns(
    'karaage.institutes.views',
    url(r'^institutes/$', 'profile_institutes', name='kg_profile_institutes'),
)
