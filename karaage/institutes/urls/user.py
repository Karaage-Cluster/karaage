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

urlpatterns = patterns('karaage.institutes.views.user',
         
    url(r'^(?P<institute_id>\d+)/users/$', 'institute_users_list', name='kg_institute_users'),
    url(r'^(?P<institute_id>\d+)/projects/$', 'institute_projects_list', name='kg_institute_projects'),
                       
)
