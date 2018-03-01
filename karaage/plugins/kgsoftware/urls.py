# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
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

from django.conf.urls import include, url

from karaage.plugins.kgsoftware import views


urlpatterns = [
    url(r'^$', views.software_list, name='kg_software_list'),
    url(r'^add/$', views.add_package, name='kg_software_add'),

    url(r'^categories/$',
        views.category_list, name='kg_software_category_list'),
    url(r'^categories/add/$',
        views.category_create, name='kg_software_category_create'),
    url(r'^categories/(?P<category_id>\d+)/edit/$',
        views.category_edit, name='kg_software_category_edit'),

    url(r'^(?P<software_id>\d+)/$',
        views.software_detail, name='kg_software_detail'),
    url(r'^(?P<software_id>\d+)/edit/$',
        views.software_edit, name='kg_software_edit'),
    url(r'^(?P<software_id>\d+)/delete/$',
        views.software_delete, name='kg_software_delete'),
    url(r'^(?P<software_id>\d+)/logs/$',
        views.software_logs, name='kg_software_logs'),
    url(r'^(?P<software_id>\d+)/add_comment/$',
        views.add_comment, name='kg_software_add_comment'),
    url(r'^(?P<software_id>\d+)/add_license/$',
        views.add_license, name='kg_software_add_license'),
    url(r'^(?P<software_id>\d+)/add_version/$',
        views.add_version, name='kg_software_add_version'),
    url(r'^(?P<software_id>\d+)/remove/(?P<person_id>\d+)/$',
        views.remove_member, name='kg_software_remove_person'),

    url(r'^version/(?P<version_id>\d+)/edit/$',
        views.edit_version, name='kg_software_version_edit'),
    url(r'^version/(?P<version_id>\d+)/delete/$',
        views.delete_version, name='kg_software_version_delete'),

    url(r'^license/(?P<license_id>\d+)/$',
        views.license_detail, name='kg_software_license_detail'),
    url(r'^license/(?P<license_id>\d+)/edit/$',
        views.edit_license, name='kg_software_license_edit'),
    url(r'^license/(?P<license_id>\d+)/delete/$',
        views.license_delete, name='kg_software_license_delete'),

    url(r'^(?P<software_id>\d+)/print/$',
        views.license_txt, name='kg_software_license_txt'),
]

urlpatterns = [
    url(r'^software/', include(urlpatterns)),
]

profile_urlpatterns = [
    url(r'^software/$', views.profile_software, name='kg_profile_software'),
]
