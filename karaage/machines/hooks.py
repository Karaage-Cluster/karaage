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
    url(r'^accounts/', include('karaage.machines.urls.accounts')),
    url(r'^machines/', include('karaage.machines.urls.machines')),
)

profile_urlpatterns = patterns('',
    url(r'^accounts/$', 'karaage.machines.views.accounts.profile_accounts', name='kg_profile_accounts'),
)

