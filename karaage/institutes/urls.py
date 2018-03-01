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

from karaage.institutes import views


urlpatterns = [
    url(r'^$', views.institute_list, name='kg_institute_list'),
    url(r'^add/$', views.add_edit_institute, name='kg_institute_add'),

    url(r'^(?P<institute_id>\d+)/$',
        views.institute_detail, name='kg_institute_detail'),
    url(r'^(?P<institute_id>\d+)/verbose/$',
        views.institute_verbose, name='kg_institute_verbose'),
    url(r'^(?P<institute_id>\d+)/edit/$',
        views.add_edit_institute, name='kg_institute_edit'),
    url(r'^(?P<institute_id>[-.\w]+)/logs/$',
        views.institute_logs, name='kg_institute_logs'),
    url(r'^(?P<institute_id>[-.\w]+)/add_comment/$',
        views.add_comment, name='kg_institute_add_comment'),
]

profile_urlpatterns = [
    url(r'^institutes/$',
        views.profile_institutes, name='kg_profile_institutes'),
]
