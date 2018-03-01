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

import django.views.static
import django_xmlrpc.views
from django.conf import settings
from django.conf.urls import include, url

from karaage.common import get_urls
from karaage.common.views import common


# Profile URLS

profile_urlpatterns = [
]


def _load_profile_urls():
    import importlib
    global profile_urlpatterns
    modules = [
        'karaage.institutes.urls',
        'karaage.projects.urls',
        'karaage.people.urls',
        'karaage.machines.urls',
    ]
    for module_name in modules:
        module = importlib.import_module(module_name)
        profile_urlpatterns += module.profile_urlpatterns


_load_profile_urls()

for urls in get_urls("profile_urlpatterns"):
    profile_urlpatterns += urls
    del urls


# Standard URLS

urlpatterns = [
    url(r'^xmlrpc/$', django_xmlrpc.views.handle_xmlrpc),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^lookup/', include('ajax_select.urls')),

    url(r'^emails/', include('karaage.emails.urls')),
    url(r'^institutes/', include('karaage.institutes.urls')),
    url(r'^projects/', include('karaage.projects.urls')),
    url(r'^persons/', include('karaage.people.urls.persons')),
    url(r'^groups/', include('karaage.people.urls.groups')),
    url(r'^accounts/', include('karaage.machines.urls.accounts')),
    url(r'^machines/', include('karaage.machines.urls.machines')),
    url(r'^profile/', include(profile_urlpatterns)),

    url(r'^$', common.index, name='index'),
    url(r'^search/$', common.search,
        name='kg_site_search'),
    url(r'^misc/$', common.misc, name='kg_misc'),
    url(r'^logs/$', common.log_list,
        name='kg_log_list'),
    url(r'^aup/$', common.aup, name="kg_aup"),
]

for urls in get_urls("urlpatterns"):
    urlpatterns += urls
    del urls

if settings.DEBUG:
    urlpatterns += [
        url(r'^kgfiles/(?P<path>.*)$', django.views.static.serve,
            {'document_root': settings.FILES_DIR})
    ]
