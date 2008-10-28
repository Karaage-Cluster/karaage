from django.conf.urls.defaults import *

from karaage.projects.models import Project

urlpatterns = patterns('karaage.projects.views',

    url(r'^$', 'project_list', name='kg_project_list'),

    url(r'^add/$', 'add_edit_project', name='kg_add_project'),

    url(r'^pending/$', 'pending_requests'),
    url(r'^no_users/$', 'no_users', name='kg_empty_projects_list'),
    url(r'^over_quota/$', 'over_quota', name='kg_projects_over_quota'),
    url(r'^by_last_usage/$', 'project_list', {'queryset': Project.active.order_by('last_usage')}, name='kg_project_last_usage_list'),
                       
    url(r'^(?P<project_id>[-.\w]+)/$', 'project_detail', name='kg_project_detail'),
    url(r'^(?P<project_id>[-.\w]+)/edit/$', 'add_edit_project', name='kg_edit_project'),
    url(r'^(?P<project_id>[-.\w]+)/delete/$', 'delete_project', name='kg_delete_project'),  
                       
    url(r'^(?P<project_id>[-.\w]+)/remove_user/(?P<username>[-.\w]+)/$', 'remove_user', name='kg_remove_project_member'),                     
)

urlpatterns += patterns('accounts.admin.views',                   

    url(r'^(?P<object_id>[-.\w]+)/logs/$', 'log_detail', {'model': Project }),   
    url(r'^(?P<object_id>[-.\w]+)/comments/$', 'comments_detail', {'model': Project }),
)

