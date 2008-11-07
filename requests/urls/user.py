from django.conf.urls.defaults import *


urlpatterns = patterns('karaage.requests.views.user',

    url(r'^$', 'user_registration', name='user_registration'),
    url(r'^cancel/(?P<user_request_id>\d+)/$', 'cancel_user_registration'),
    url(r'^choose_project/$', 'choose_project', name='user_choose_project'),
    url(r'^created/(?P<user_request_id>\d+)/$', 'account_created', name='kg_user_account_pending'),
                        
    url(r'^approve/(?P<user_request_id>\d+)/$', 'approve_person', name='user_approve_account'),
    url(r'^reject/(?P<user_request_id>\d+)/$', 'reject_person', name='user_reject_account'),

    url(r'^(?P<user_request_id>\d+)/$', 'request_detail', name='user_account_request_detail'),
                       
)

