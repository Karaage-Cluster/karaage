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


urlpatterns = patterns('karaage.usage.views',
    url(r'^$', 'index', name='kg_usage_list'),                   
    url(r'^index/$', 'usage_index', name='kg_usage_index'),                   
    # Defaults to settings.DEFAULT_MC
    url(r'^search/$', 'search', name='kg_usage_search'),
    url(r'^project_search/$', 'project_search', name='project_usage_search'),
    url(r'^unknown/$', 'unknown_usage', name='kg_unknown_usage'),
    url(r'^top_users/$', 'top_users'),
    url(r'^core_report/$', 'core_report', name='kg_core_report'),
    url(r'^mem_report/$', 'mem_report', name='kg_mem_report'),
    url(r'^jobs/$', 'job_list', name='kg_job_list'),
    url(r'^jobs/(?P<jobid>[-.\w]+)/$', 'job_detail', name='kg_job_detail'),
    url(r'^institute/trends/$', 'institute_trends'),
    url(r'^institute/(?P<institute_id>\d+)/users/$', 'institute_users'),
    url(r'^(?P<machine_category_id>\d+)/institute/(?P<institute_id>\d+)/users/$', 'institute_users'),        
    url(r'^institute/(?P<institute_id>\d+)/$', 'institute_usage', name='kg_institute_usage'),

    url(r'^institute/(?P<institute_id>\d+)/$', 'institute_usage', name='kg_usage_institute'),
    url(r'^projects/(?P<project_id>[-.\w]+)/$', 'project_usage', name='kg_usage_project'),
                           
    url(r'^(?P<machine_category_id>\d+)/$', 'index', name='kg_mc_usage'),
    url(r'^(?P<machine_category_id>\d+)/institute/(?P<institute_id>\d+)/$', 'institute_usage', name='kg_usage_institute'),
    url(r'^(?P<machine_category_id>\d+)/institute/(?P<institute_id>\d+)/(?P<project_id>[-.\w]+)/$', 'project_usage'),
                                             
    url(r'^(?P<machine_category_id>\d+)/top_users/$', 'top_users'),
    url(r'^(?P<machine_category_id>\d+)/top_users/(?P<count>\d+)/$', 'top_users'),
                       
)
