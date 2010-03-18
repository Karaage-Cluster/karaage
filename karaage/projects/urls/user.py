from django.conf.urls.defaults import *


urlpatterns = patterns('karaage.projects.views.user',           

    url(r'^add/$', 'add_edit_project', name='kg_project_add'),                    
    url(r'^(?P<project_id>[-.\w]+)/$', 'project_detail', name='kg_project_detail'),
    url(r'^(?P<project_id>[-.\w]+)/edit/$', 'add_edit_project', name='kg_project_edit'),

        
)
urlpatterns += patterns('karaage.projects.views.admin',
                        
    url(r'^(?P<project_id>[-.\w]+)/remove_user/(?P<username>[-.\w]+)/$', 'remove_user', name='kg_remove_project_member'), 

)
