from django.conf.urls.defaults import *


urlpatterns = patterns('karaage.requests.views.projects',           
    url(r'^$', 'project_registration', name='project_registration'),
    url(r'^created/(?P<project_request_id>\d+)/$', 'project_created', name='project_created'),
    url(r'^approve/(?P<project_request_id>\d+)/$', 'approve_project', name='user_approve_project'),
    url(r'^reject/(?P<project_request_id>\d+)/$', 'reject_project', name='user_reject_project'),

    url(r'^(?P<project_request_id>\d+)/$', 'request_detail', name='user_project_request_detail'),
    
)
