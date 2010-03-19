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

from django.conf.urls.defaults import *


urlpatterns = patterns('karaage.pbsmoab.views',
      
    url(r'^projectchunk/(?P<project_id>[-.\w]+)/$', 'projectchunk_edit', name='kg_projectchunk_edit'),
    url(r'^projects_by_cap_used/$', 'projects_by_cap_used', name='kg_projects_by_cap_used'),
)
