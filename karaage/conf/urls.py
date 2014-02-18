# Copyright 2007-2013 VPAC
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
from django.conf import settings

urlpatterns = patterns('',
    url(r'^$', 'karaage.common.views.index', name='index'),
    url(r'^search/$', 'karaage.common.views.search', name='kg_site_search'),
    url(r'^misc/$', 'karaage.common.views.misc', name='kg_misc'),
    url(r'^logs/$', 'karaage.common.views.log_list', name='kg_log_list'),

    url(r'^persons/', include('karaage.people.urls.persons')),
    url(r'^profile/', include('karaage.people.urls.profile')),
    url(r'^groups/', include('karaage.people.urls.groups')),
    url(r'^institutes/', include('karaage.institutes.urls')),
    url(r'^projects/', include('karaage.projects.urls')),
    url(r'^machines/', include('karaage.machines.urls')),
    url(r'^usage/', include('karaage.usage.urls')),
    url(r'^software/', include('karaage.software.urls')),
    url(r'^applications/', include('karaage.applications.urls')),
    url(r'^xmlrpc/$', 'django_xmlrpc.views.handle_xmlrpc',),

    url(r'^aup/$', 'karaage.legacy.simple.direct_to_template', {'template': 'aup.html'}, name="aup"),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^lookup/', include('ajax_select.urls')),
    url(r'^emails/', include('karaage.emails.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^karaage_graphs/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.GRAPH_ROOT}),
    )
