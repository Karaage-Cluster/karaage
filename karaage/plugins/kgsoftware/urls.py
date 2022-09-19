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

from django.urls import include, re_path

from karaage.plugins.kgsoftware import views


urlpatterns = [
    re_path(r"^$", views.software_list, name="kg_software_list"),
    re_path(r"^add/$", views.add_package, name="kg_software_add"),
    re_path(r"^categories/$", views.category_list, name="kg_software_category_list"),
    re_path(r"^categories/add/$", views.category_create, name="kg_software_category_create"),
    re_path(r"^categories/(?P<category_id>\d+)/edit/$", views.category_edit, name="kg_software_category_edit"),
    re_path(r"^(?P<software_id>\d+)/$", views.software_detail, name="kg_software_detail"),
    re_path(r"^(?P<software_id>\d+)/edit/$", views.software_edit, name="kg_software_edit"),
    re_path(r"^(?P<software_id>\d+)/delete/$", views.software_delete, name="kg_software_delete"),
    re_path(r"^(?P<software_id>\d+)/logs/$", views.software_logs, name="kg_software_logs"),
    re_path(r"^(?P<software_id>\d+)/add_comment/$", views.add_comment, name="kg_software_add_comment"),
    re_path(r"^(?P<software_id>\d+)/add_license/$", views.add_license, name="kg_software_add_license"),
    re_path(r"^(?P<software_id>\d+)/add_version/$", views.add_version, name="kg_software_add_version"),
    re_path(
        r"^(?P<software_id>\d+)/remove/(?P<person_id>\d+)/$", views.remove_member, name="kg_software_remove_person"
    ),
    re_path(r"^version/(?P<version_id>\d+)/edit/$", views.edit_version, name="kg_software_version_edit"),
    re_path(r"^version/(?P<version_id>\d+)/delete/$", views.delete_version, name="kg_software_version_delete"),
    re_path(r"^license/(?P<license_id>\d+)/$", views.license_detail, name="kg_software_license_detail"),
    re_path(r"^license/(?P<license_id>\d+)/edit/$", views.edit_license, name="kg_software_license_edit"),
    re_path(r"^license/(?P<license_id>\d+)/delete/$", views.license_delete, name="kg_software_license_delete"),
    re_path(r"^(?P<software_id>\d+)/print/$", views.license_txt, name="kg_software_license_txt"),
]

urlpatterns = [
    re_path(r"^software/", include(urlpatterns)),
]

profile_urlpatterns = [
    re_path(r"^software/$", views.profile_software, name="kg_profile_software"),
]
