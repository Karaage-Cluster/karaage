from django.conf.urls.defaults import *

from models import Machine

info_dict = {
    'model': Machine,
    }


urlpatterns = patterns('django.views.generic.create_update',                        url(r'^add/$', 'create_object', info_dict),    
    url(r'^(?P<object_id>\d+)/edit/$', 'update_object', info_dict),
        
)

urlpatterns += patterns('karaage.machines.views',

    url(r'^$', 'index', name='kg_machine_list'),
    url(r'^(?P<machine_id>\d+)/$', 'machine_detail', name='kg_machine_detail'),
    url(r'^(?P<machine_id>\d+)/user_accounts/$', 'machine_accounts'),
    url(r'^(?P<machine_id>\d+)/projects/$', 'machine_projects'),
)
                  
