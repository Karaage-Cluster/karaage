from django.conf.urls import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('karaage.people.views.user',
    url(r'^profile/$', 'profile', name='kg_user_profile'),
    url(r'^profile/accounts/$', 'profile_accounts', name='kg_user_profile_accounts'),
    url(r'^profile/software/$', 'profile_software', name='kg_user_profile_software'),
    url(r'^profile/edit/$', 'edit_profile', name='kg_profile_edit'),
    url(r'^login/$', 'login', name='login'),
    url(r'^change_password/$', 'password_change', name='kg_user_change_password'),
    url(r'^change_password/done/$', 'password_change_done', name='kg_user_password_done'),               

)

urlpatterns += patterns('',
    url(r'^$', 'django.views.generic.simple.redirect_to', {'url': '/users/apply/'}),
    (r'^users/', include('karaage.people.urls.user')),
    (r'^institutes/', include('karaage.institutes.urls.user')),
    (r'^projects/', include('karaage.projects.urls.user')),
    (r'^software/', include('karaage.software.urls.user')),
    (r'^reports/', include('karaage.projectreports.urls.user')),
    (r'^applications/', include('karaage.applications.urls.user')),
    (r'xmlrpc/$', 'django_xmlrpc.views.handle_xmlrpc',),
    (r'^pbs/', include('django_pbs.servers.urls')),
    url(r'^captcha/', include('captcha.urls')), 

)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^accounts/login/$', 'login', name='login'),
    url(r'^accounts/logout/$', 'logout', name='logout'),

)


if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^ingress_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )		


