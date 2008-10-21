from django.conf.urls.defaults import *


urlpatterns = patterns('accounts.user.users.views',

    url(r'^(?P<username>[-.\w]+)/$', 'user_detail', name='ac_user_detail'),
    url(r'^(?P<username>[-.\w]+)/flag_left/$', 'flag_left'),
                       
)

urlpatterns += patterns('accounts.admin.users.views',
                        
    url(r'^accounts/(?P<useraccount_id>\d+)/makedefault/(?P<project_id>[-.\w]+)/$', 'make_default', name='user_make_default'),
)
