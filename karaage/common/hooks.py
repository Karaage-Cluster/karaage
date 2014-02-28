# Copyright 2007-2014 VPAC
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

urlpatterns = patterns('',
    url(r'^$', 'karaage.common.views.common.index', name='index'),
    url(r'^search/$', 'karaage.common.views.common.search', name='kg_site_search'),
    url(r'^misc/$', 'karaage.common.views.common.misc', name='kg_misc'),
    url(r'^logs/$', 'karaage.common.views.common.log_list', name='kg_log_list'),
    url(r'^aup/$', 'karaage.common.views.common.aup', name="kg_aup"),
    url(r'^profile/', include('karaage.common.urls.profile')),
)
