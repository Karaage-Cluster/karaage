from django.conf.urls.defaults import *

from models import Machine

info_dict = {
    'model': Machine,
    'template_name': 'machines/machine_form.html',
    }

urlpatterns = patterns('accounts.main.generic_views',
                       
    url(r'^add/$', 'add_edit', info_dict),    
    url(r'^(?P<object_id>\d+)/edit/$', 'add_edit', info_dict),                     
)


urlpatterns += patterns('karaage.machines.views',

    url(r'^$', 'index', name='kg_machine_list'),
    url(r'^(?P<machine_id>\d+)/$', 'machine_detail', name='kg_machine_detail'),
    url(r'^(?P<machine_id>\d+)/user_accounts/$', 'machine_accounts'),
    url(r'^(?P<machine_id>\d+)/projects/$', 'machine_projects'),
)
                        
