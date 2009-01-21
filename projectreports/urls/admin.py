from django.conf.urls.defaults import *


urlpatterns = patterns('karaage.projectreports.views.admin',

                       
    url(r'^$', 'report_list', name='kg_projectreport_list'),
    url(r'^(?P<report_id>\d+)/$', 'report_detail', name='kg_projectreport_detail'),
)
