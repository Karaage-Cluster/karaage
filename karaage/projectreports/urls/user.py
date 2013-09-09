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


urlpatterns = patterns('karaage.projectreports.views.user',

    url(r'^(?P<project_id>[-.\w]+)/$', 'survey', name='kg_survey'),
    url(r'^(?P<project_id>[-.\w]+)/thanks/$', 'thanks', name='kg_survey_thanks'),

)

                        
