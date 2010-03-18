from django.conf.urls.defaults import *


urlpatterns = patterns('karaage.people.views.user',

    url(r'^(?P<username>[-.\w]+)/$', 'user_detail', name='kg_user_detail'),
    url(r'^(?P<username>[-.\w]+)/flag_left/$', 'flag_left'),
                       
)

urlpatterns += patterns('karaage.people.views.admin',
                        
    url(r'^accounts/(?P<useraccount_id>\d+)/makedefault/(?P<project_id>[-.\w]+)/$', 'make_default', name='kg_user_make_default'),
)
