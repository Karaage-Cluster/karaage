from django.conf.urls.defaults import *
from django.conf import settings

from karaage.software.models import SoftwarePackage, SoftwareCategory, SoftwareLicense

info_dict = {
    'model': SoftwarePackage,
    'template_name': 'software/package_form.html',
    }
c_info_dict = {
    'model': SoftwareCategory,
    'template_name': 'software/category_form.html',
    }


urlpatterns = patterns('accounts.main.generic_views',
                       
    (r'^(?P<object_id>\d+)/edit/$', 'add_edit', info_dict),
    (r'^categories/add/$', 'add_edit', c_info_dict),    
    (r'^categories/(?P<object_id>\d+)/edit/$', 'add_edit', c_info_dict),
                 
)


urlpatterns += patterns('karaage.software.views.admin',

                       
    url(r'^$', 'software_list', name='kg_software_list'),
    url(r'^add/$', 'add_package', name='kg_software_add'),
    url(r'^categories/$', 'category_list', name='kg_software_category_list'),
                        
    url(r'^(?P<package_id>\d+)/$', 'software_detail', name='kg_software_detail'),
    (r'^(?P<package_id>\d+)/remove/(?P<user_id>\d+)/$', 'remove_member'),
    (r'^(?P<package_id>\d+)/license/add/$', 'add_edit_license'),
    (r'^(?P<package_id>\d+)/license/edit/(?P<license_id>\d+)/$', 'add_edit_license'),
    (r'^(?P<package_id>\d+)/version/add/$', 'add_edit_version'),
    (r'^(?P<package_id>\d+)/version/edit/(?P<version_id>\d+)/$', 'add_edit_version'),
    (r'^(?P<package_id>\d+)/version/delete/(?P<version_id>\d+)/$', 'delete_version'),
                        
    (r'^license/(?P<license_id>\d+)/$', 'license_detail'),
    (r'^(?P<license_id>\d+)/$', 'license_detail'),
)
                        


urlpatterns += patterns('karaage.views',                   

    url(r'^(?P<object_id>\d+)/logs/$', 'log_detail', {'model': SoftwarePackage }, name='kg_software_logs'),
)
