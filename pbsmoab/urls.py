from django.conf.urls.defaults import *


urlpatterns = patterns('karaage.pbsmoab.views',

    url(r'^projectchunk/(?P<project_id>[-.\w]+)/$', 'projectchunk_edit', name='kg_projectchunk_edit'),
)
