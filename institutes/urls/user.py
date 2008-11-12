from django.conf.urls.defaults import *

urlpatterns = patterns('karaage.institutes.views.user',
         
    url(r'^(?P<institute_id>\d+)/users/$', 'institute_users_list', name='kg_institute_users'),
    url(r'^(?P<institute_id>\d+)/projects/$', 'institute_projects_list', name='kg_institute_projects'),
                       
)
