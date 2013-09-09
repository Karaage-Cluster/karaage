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

from karaage.pbsmoab.models import InstituteChunk


iq_info_dict = {
    'model': InstituteChunk,
    }



urlpatterns = patterns('karaage.legacy.create_update', 
    url(r'^institutechunk/(?P<object_id>\d+)/$', 'update_object', iq_info_dict, name='kg_institute_quota_edit'),
                 
)

urlpatterns += patterns('karaage.institutes.views.admin',

    url(r'^$', 'institute_list', name='kg_institute_list'),
    url(r'^add/$', 'add_edit_institute', name='kg_institute_add'),
    url(r'^(?P<institute_id>\d+)/$', 'institute_detail', name='kg_institute_detail'),
    url(r'^(?P<institute_id>\d+)/verbose/$', 'institute_verbose', name='kg_institute_verbose'),
    url(r'^(?P<institute_id>\d+)/edit/$', 'add_edit_institute', name='kg_institute_edit'),
    url(r'^(?P<institute_id>\d+)/$', 'institute_detail', name='kg_institute_users'),
    url(r'^(?P<institute_id>\d+)/$', 'institute_detail', name='kg_institute_projects'),
)
                  
