from django.conf.urls.defaults import *

from karaage.people.models import Institute
from karaage.institutes.models import InstituteQuota

info_dict = {
    'model': Institute,
    'template_name': 'institutes/institute_form.html',
    }

iq_info_dict = {
    'model': InstituteQuota,
    'template_name': 'institutes/institutequota_form.html',
    }



urlpatterns = patterns('accounts.main.generic_views',
    url(r'^institutequota/(?P<object_id>\d+)/$', 'add_edit', iq_info_dict, name='ac_institute_quota_edit'),
    url(r'^add/$', 'add_edit', info_dict, name='ac_institute_add'),                  
    url(r'^(?P<object_id>\d+)/edit/$', 'add_edit', info_dict, name='ac_institute_edit'),   
                 
)

urlpatterns += patterns('karaage.institutes.views.admin',

    url(r'^$', 'institute_list', name='kg_institute_list'),
    url(r'^(?P<institute_id>\d+)/$', 'institute_detail', name='kg_institute_detail'),
    url(r'^(?P<institute_id>\d+)/$', 'institute_detail', name='kg_institute_users'),
    url(r'^(?P<institute_id>\d+)/$', 'institute_detail', name='kg_institute_projects'),
)
                  
