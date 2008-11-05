from django.conf.urls.defaults import *

urlpatterns = patterns('karaage.requests.views.admin',

    url(r'^$', 'account_request_list', name='kg_account_request_list'),
    url(r'^(?P<ar_id>\d+)/$', 'account_request_detail', name='kg_account_request_detail'),
    url(r'^(?P<ar_id>\d+)/approve/$', 'account_request_approve', name='kg_account_approve'),
    url(r'^(?P<ar_id>\d+)/reject/$', 'account_request_reject', name='kg_account_reject'),

)
