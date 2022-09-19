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
from django.conf import settings
from django.urls import include, re_path

from karaage.common import get_urls
from karaage.common.views import common


# Profile URLS

profile_urlpatterns = []


def _load_profile_urls():
    import importlib

    global profile_urlpatterns
    modules = [
        "karaage.institutes.urls",
        "karaage.projects.urls",
        "karaage.people.urls",
        "karaage.machines.urls",
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
    re_path(r"^captcha/", include("captcha.urls")),
    re_path(r"^lookup/", include("ajax_select.urls")),
    re_path(r"^emails/", include("karaage.emails.urls")),
    re_path(r"^institutes/", include("karaage.institutes.urls")),
    re_path(r"^projects/", include("karaage.projects.urls")),
    re_path(r"^persons/", include("karaage.people.urls.persons")),
    re_path(r"^groups/", include("karaage.people.urls.groups")),
    re_path(r"^accounts/", include("karaage.machines.urls.accounts")),
    re_path(r"^machines/", include("karaage.machines.urls.machines")),
    re_path(r"^profile/", include(profile_urlpatterns)),
    re_path(r"^$", common.index, name="index"),
    re_path(r"^search/$", common.search, name="kg_site_search"),
    re_path(r"^misc/$", common.misc, name="kg_misc"),
    re_path(r"^logs/$", common.log_list, name="kg_log_list"),
    re_path(r"^aup/$", common.aup, name="kg_aup"),
]

for urls in get_urls("urlpatterns"):
    urlpatterns += urls
    del urls

if settings.DEBUG:
    urlpatterns += [
        re_path(r"^kgfiles/(?P<path>.*)$", django.views.static.serve, {"document_root": settings.FILES_DIR})
    ]
