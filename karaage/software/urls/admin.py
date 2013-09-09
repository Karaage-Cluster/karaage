# Copyright 2007-2013 VPAC
#
# This file is part of Karaage.
#
# Karaage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Karaage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Karaage  If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls import *

from karaage.software.models import SoftwarePackage, SoftwareCategory, SoftwareLicense

info_dict = {
    'model': SoftwarePackage,
    }
d_info_dict = {
    'model': SoftwarePackage,
    'post_delete_redirect':  '/',
    }
d_license_dict = {
    'model': SoftwareLicense,
    'post_delete_redirect': '/',
    }
c_info_dict = {
    'model': SoftwareCategory,
    }


urlpatterns = patterns('karaage.legacy.create_update',                        
    url(r'^(?P<object_id>\d+)/edit/$', 'update_object', info_dict, name='kg_softwarepackage_edit'),
    url(r'^(?P<object_id>\d+)/delete/$', 'delete_object', d_info_dict, name='kg_softwarepackage_delete'),
    url(r'^categories/add/$', 'create_object', c_info_dict),    
    url(r'^categories/(?P<object_id>\d+)/edit/$', 'update_object', c_info_dict),
    url(r'^license/(?P<object_id>\d+)/delete/$', 'delete_object', d_license_dict, name='kg_softwarelicense_delete'),
)


urlpatterns += patterns('karaage.software.views.admin',

                       
    url(r'^$', 'software_list', name='kg_software_list'),
    url(r'^add/$', 'add_package', name='kg_software_add'),
    url(r'^categories/$', 'category_list', name='kg_software_category_list'),
    url(r'^requests/$', 'softwarerequest_list', name='kg_softwarerequest_list'),
    url(r'^requests/(?P<softwarerequest_id>\d+)/approve/$', 'softwarerequest_approve', name='kg_softwarerequest_approve'),
    url(r'^requests/(?P<softwarerequest_id>\d+)/decline/$', 'softwarerequest_delete', name='kg_softwarerequest_delete'),
                        
    url(r'^(?P<package_id>\d+)/$', 'software_detail', name='kg_software_detail'),
    url(r'^(?P<package_id>\d+)/verbose/$', 'software_verbose', name='kg_software_verbose'),
    url(r'^(?P<package_id>\d+)/stats/$', 'software_stats', name='kg_software_stats'),
    url(r'^(?P<package_id>\d+)/remove/(?P<user_id>\d+)/$', 'remove_member', name='kg_software_removeuser'),
    url(r'^(?P<package_id>\d+)/license/add/$', 'add_edit_license', name='kg_softwarelicense_add'),
    url(r'^(?P<package_id>\d+)/license/edit/(?P<license_id>\d+)/$', 'add_edit_license', name='kg_softwarelicense_edit'),
    url(r'^(?P<package_id>\d+)/version/add/$', 'add_edit_version', name='kg_softwareversion_add'),
    url(r'^(?P<package_id>\d+)/version/edit/(?P<version_id>\d+)/$', 'add_edit_version', name='kg_softwareversion_edit'),
    url(r'^(?P<package_id>\d+)/version/stats/(?P<version_id>\d+)/$', 'version_stats', name='kg_softwareversion_stats'),
    url(r'^(?P<package_id>\d+)/version/delete/(?P<version_id>\d+)/$', 'delete_version', name='kg_softwareversion_delete'),
                        
    url(r'^license/(?P<license_id>\d+)/$', 'license_detail', name='kg_softwarelicense_detail'),
)
                        


urlpatterns += patterns('karaage.views',                   

    url(r'^(?P<object_id>\d+)/logs/$', 'log_detail', {'model': SoftwarePackage }, name='kg_software_logs'),
)
