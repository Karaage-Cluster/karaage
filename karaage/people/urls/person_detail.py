# Copyright 2008, 2010, 2013-2015 VPAC
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
    'karaage.people.views.persons',
    url(r'^$', 'user_detail', name='kg_person_detail'),
    url(r'^verbose/$', 'user_verbose', name='kg_person_verbose'),
    url(r'^activate/$', 'activate', name='kg_person_activate'),
    url(r'^delete/$', 'delete_user', name='kg_person_delete'),
    url(r'^password/$', 'password_change', name='kg_person_password'),
    url(r'^lock/$', 'lock_person', name='kg_person_lock'),
    url(r'^unlock/$', 'unlock_person', name='kg_person_unlock'),
    url(r'^bounced_email/$', 'bounced_email', name='kg_person_bounce'),
    url(r'^logs/$', 'person_logs', name='kg_person_logs'),
    url(r'^add_comment/$', 'add_comment', name='kg_person_add_comment'),
    url(r'^edit/$', 'edit_user', name='kg_person_edit'),
    url(r'^password_request/$', 'password_request', name='kg_person_reset'),
    url(r'^password_request/done/$',
        'password_request_done', name='kg_person_reset_done'),
)
