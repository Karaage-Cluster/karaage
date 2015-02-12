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

from django.conf.urls import patterns, url, include

from .views.project import register as register_project
register_project()

urlpatterns = patterns(
    'karaage.plugins.kgapplications.views',
    url(r'^$',
        'common.application_list', name='kg_application_list'),
    url(r'^applicants/(?P<applicant_id>\d+)/$',
        'common.applicant_edit', name='kg_applicant_edit'),
    url(r'^(?P<application_id>\d+)/logs/$',
        'common.application_logs', name='kg_application_logs'),
    url(r'^(?P<application_id>\d+)/add_comment/$',
        'common.add_comment', name='kg_application_add_comment'),

    url(r'^(?P<application_id>\d+)/$',
        'common.application_detail', name='kg_application_detail'),
    url(r'^(?P<application_id>\d+)/(?P<state>[-.\w]+)/$',
        'common.application_detail', name='kg_application_detail'),
    url(r'^(?P<application_id>\d+)/(?P<state>[-.\w]+)/(?P<label>[-.\w]+)/$',
        'common.application_detail', name='kg_application_detail'),

    url(r'^project/new/$',
        'project.new_application', name='kg_application_new'),
    url(r'^project/invite/$',
        'project.send_invitation', name='kg_application_invite'),
    url(r'^project/invite/(?P<project_id>\d+)/$',
        'project.send_invitation', name='kg_application_invite'),

    # this must come last
    url(r'^(?P<token>[-.\w]+)/$',
        'common.application_unauthenticated',
        name='kg_application_unauthenticated'),
    url(r'^(?P<token>[-.\w]+)/(?P<state>[-.\w]+)/$',
        'common.application_unauthenticated',
        name='kg_application_unauthenticated'),
    url(r'^(?P<token>[-.\w]+)/(?P<state>[-.\w]+)/(?P<label>[-.\w]+)/$',
        'common.application_unauthenticated',
        name='kg_application_unauthenticated'),
)

urlpatterns = patterns(
    '',
    url(r'^applications/', include(urlpatterns)),
)

profile_urlpatterns = patterns(
    'karaage.plugins.kgapplications.views',
    url(r'^applications/$',
        'common.profile_application_list',
        name='kg_profile_applications'),
)
