from django.conf.urls.defaults import *


urlpatterns = patterns('karaage.pbsmoab.views',
      
    url(r'^projectchunk/(?P<project_id>[-.\w]+)/$', 'projectchunk_edit', name='kg_projectchunk_edit'),
    url(r'^projects_by_cap_used/$', 'projects_by_cap_used', name='kg_projects_by_cap_used'),
)
