from django.conf.urls import *

import ajax_select.urls

urlpatterns = patterns('',
    url(r'^$', 'karaage.views.admin_index', name='index'),
    url(r'^search/$', 'karaage.views.search', name='kg_site_search'), 

    url(r'^people/', include('karaage.people.urls.admin')),
    url(r'^profile/', include('karaage.people.urls.profile')),
    url(r'^institutes/', include('karaage.institutes.urls.admin')),
    url(r'^projects/', include('karaage.projects.urls.admin')),
    url(r'^machines/', include('karaage.machines.urls')),
    url(r'^usage/', include('karaage.usage.urls.admin')),
    url(r'^software/', include('karaage.software.urls.admin')),
    url(r'^projectreports/', include('karaage.projectreports.urls.admin')),
    url(r'^surveys/', include('django_surveys.urls')),
    url(r'^pbsmoab/', include('karaage.pbsmoab.urls')),
    url(r'^emails/', include('karaage.emails.urls')),
    url(r'^applications/', include('karaage.applications.urls.admin')),

    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^pbs/', include('django_pbs.servers.urls')),
    url(r'^misc/$', 'karaage.legacy.simple.direct_to_template', {'template': 'misc/index.html'}),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', name='logout'),

    url(r'^lookup/', include(ajax_select.urls)),

    url(r'^logs/$', 'karaage.admin.views.log_list', name='kg_log_list'),
)

