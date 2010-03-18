from django.conf.urls.defaults import *


urlpatterns = patterns('karaage.software.views.user',

    url(r'^add/$', 'add_package_list', name='kg_software_list'),
    url(r'^add/(?P<package_id>\d+)/$', 'add_package'),
    url(r'^add/(?P<package_id>\d+)/print/$', 'license_txt'),
)
                        
