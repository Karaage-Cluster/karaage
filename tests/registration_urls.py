from django.conf.urls import *
from django.conf import settings

urlpatterns = patterns('',
    url(r'^$', 'karaage.legacy.simple.direct_to_template', {'template': 'site_search.html'}, name='index'),
    url(r'^profile/', include('karaage.people.urls.profile')),
    (r'^people/', include('karaage.people.urls.user')),
    (r'^institutes/', include('karaage.institutes.urls.user')),
    (r'^projects/', include('karaage.projects.urls.user')),
    (r'^software/', include('karaage.software.urls.user')),
    (r'^applications/', include('karaage.applications.urls.user')),
    (r'xmlrpc/$', 'django_xmlrpc.views.handle_xmlrpc',),
    url(r'^captcha/', include('captcha.urls')),
)
