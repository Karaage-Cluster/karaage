from django.conf.urls.defaults import *


urlpatterns = patterns('karaage.usage.views',
    url(r'^$', 'index', name='kg_usage_list'),                   
    # Defaults to settings.DEFAULT_MC
    url(r'^search/$', 'search', name='kg_usage_search'),
    url(r'^project_search/$', 'project_search', name='project_usage_search'),
    url(r'^unknown/$', 'unknown_usage', name='kg_unknown_usage'),
    url(r'^top_users/$', 'top_users'),
    url(r'^institute/trends/$', 'institute_trends'),
    url(r'^institute/(?P<institute_id>\d+)/users/$', 'institute_users'),
    url(r'^(?P<machine_category_id>\d+)/institute/(?P<institute_id>\d+)/users/$', 'institute_users'),        
    url(r'^institute/(?P<institute_id>\d+)/$', 'institute_usage', name='kg_institute_usage'),
    url(r'^institute/(?P<institute_id>\d+)/(?P<project_id>[-.\w]+)/$', 'project_usage', name='kg_project_usage'),
    #(r'^(?P<project_id>[-.\w]+)/$', 'project_usage'),
                           
    url(r'^(?P<machine_category_id>\d+)/$', 'index', name='kg_mc_usage'),
    url(r'^(?P<machine_category_id>\d+)/institute/(?P<institute_id>\d+)/$', 'institute_usage', name='kg_usage_institute'),
    url(r'^(?P<machine_category_id>\d+)/institute/(?P<institute_id>\d+)/(?P<project_id>[-.\w]+)/$', 'project_usage'),
                                             
    url(r'^(?P<machine_category_id>\d+)/top_users/$', 'top_users'),
    url(r'^(?P<machine_category_id>\d+)/top_users/(?P<count>\d+)/$', 'top_users'),
                       
)
