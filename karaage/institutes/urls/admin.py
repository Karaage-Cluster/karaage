from django.conf.urls.defaults import *

from karaage.people.models import Institute
from karaage.pbsmoab.models import InstituteChunk

info_dict = {
    'model': Institute,
    }

iq_info_dict = {
    'model': InstituteChunk,
    }



urlpatterns = patterns('django.views.generic.create_update', 
    url(r'^institutechunk/(?P<object_id>\d+)/$', 'update_object', iq_info_dict, name='kg_institute_quota_edit'),
    url(r'^add/$', 'create_object', info_dict, name='kg_institute_add'),                  
    url(r'^(?P<object_id>\d+)/edit/$', 'update_object', info_dict, name='kg_institute_edit'),   
                 
)

urlpatterns += patterns('karaage.institutes.views.admin',

    url(r'^$', 'institute_list', name='kg_institute_list'),
    url(r'^(?P<institute_id>\d+)/$', 'institute_detail', name='kg_institute_detail'),
    url(r'^(?P<institute_id>\d+)/$', 'institute_detail', name='kg_institute_users'),
    url(r'^(?P<institute_id>\d+)/$', 'institute_detail', name='kg_institute_projects'),
)
                  
