from django.conf.urls.defaults import *
from django.conf import settings
from karaage.people.models import Person

urlpatterns = patterns('karaage.people.views.admin',


    url(r'^index/$', 'index', name='kg_trouble_shooting_list'),
                       
    url(r'^$', 'user_list', name='kg_user_list'),
    url(r'^deleted/$', 'user_list', { 'queryset': Person.deleted.all(),}),
    url(r'^last_used/$', 'user_list', { 'queryset': Person.active.order_by('last_usage'),}),

    url(r'^struggling/$', 'struggling', name='kg_struggling_users_list'),

                   
    url(r'^no_default/$', 'no_default_list', name='ac_no_default_list'),
    url(r'^wrong_default/$', 'wrong_default_list', name='ac_wrong_default_list'),
    url(r'^no_account/$', 'no_account_list', name='ac_no_account_list'),
    url(r'^locked/$', 'locked_list', name='ac_locked_users_list'),
    url(r'^add/$', 'add_edit_user', name='admin_add_user'),
    url(r'^accounts/(?P<useraccount_id>\d+)/change_shell/$', 'change_shell', name='kg_change_shell'),
    url(r'^accounts/(?P<useraccount_id>\d+)/edit/$', 'add_edit_useraccount'),
    url(r'^accounts/(?P<useraccount_id>\d+)/delete/$', 'delete_useraccount', name='admin_delete_account'),
                       
    url(r'^accounts/(?P<useraccount_id>\d+)/makedefault/(?P<project_id>[-.\w]+)/$', 'make_default', name='admin_make_default'),


    (r'^(?P<username>[-.\w]+)/', include('karaage.people.urls.admin_user_detail')),                   

)

                        

urlpatterns += patterns('karaage.views',                   

    url(r'^(?P<object_id>\d+)/logs/$', 'log_detail', {'model': Person }, name='ac_userlogs'),
)
