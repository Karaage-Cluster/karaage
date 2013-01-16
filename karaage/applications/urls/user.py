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


urlpatterns = patterns('karaage.applications.views',

    url(r'^$', 'user.application_index', name='kg_application_index'),
    url(r'^pending/$', 'user.pending_applications', name='kg_application_pendinglist'),
    url(r'^new-user/$', 'user.do_userapplication', name='kg_new_userapplication'),
    url(r'^new-project/$', 'projects.do_projectapplication', name='kg_new_projectapplication'),
    url(r'^choose-project/$', 'user.choose_project', name='kg_choose_project_existing'),
    url(r'^saml/new-user/$', 'user.do_userapplication', {'saml': True}, name='kg_saml_new_userapplication'),
    url(r'^saml/new-project/$', 'projects.do_projectapplication', {'saml': True}, name='kg_saml_new_projectapplication'),
    url(r'^saml/(?P<token>.+)/do/$', 'user.do_userapplication', {'saml': True}, name='kg_saml_invited_userapplication'),
    url(r'^invite/(?P<project_id>[-.\w]+)/$', 'user.send_invitation', name='kg_userapplication_invite'),

    url(r'^projects/add/$', 'projects.projectapplication_existing', name='kg_projectapplication_existing'),
    url(r'^projects/(?P<application_id>\d+)/$', 'projects.approve_projectapplication', name='kg_projectapplication_detail'),
    url(r'^projects/(?P<application_id>\d+)/complete/$', 'projects.projectapplication_complete', name='kg_projectapplication_complete'),
    url(r'^projects/(?P<application_id>\d+)/pending/$', 'projects.projectapplication_pending', name='kg_projectapplication_pending'),
    url(r'^projects/(?P<application_id>\d+)/decline/$', 'projects.decline_projectapplication', name='kg_projectapplication_decline'),
    url(r'^(?P<application_id>\d+)/$', 'user.approve_userapplication', name='kg_userapplication_detail'),
    url(r'^(?P<application_id>\d+)/approve/$', 'user.approve_userapplication', name='kg_userapplication_approve'),
    url(r'^(?P<application_id>\d+)/decline/$', 'user.decline_userapplication', name='kg_userapplication_decline'),
    url(r'^(?P<application_id>\d+)/complete/$', 'user.userapplication_complete', name='kg_userapplication_complete'),
    url(r'^(?P<application_id>\d+)/pending/$', 'user.userapplication_pending', name='kg_userapplication_pending'),

    url(r'^(?P<token>.+)/start/$', 'user.start_invite_application', name='kg_application_start_invite'),
    url(r'^(?P<token>.+)/choose_project/$', 'user.choose_project', name='kg_application_choose_project'),
    url(r'^(?P<token>.+)/cancel/$', 'user.cancel', name='kg_application_cancel'),
    url(r'^(?P<token>.+)/done/$', 'user.application_done', name='kg_application_done'),
    url(r'^(?P<token>.+)/do/$', 'user.do_userapplication', name='kg_invited_userapplication'),

)
