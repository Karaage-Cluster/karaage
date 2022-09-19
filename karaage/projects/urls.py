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

from django.conf import settings
from django.urls import re_path

from karaage.projects import views


urlpatterns = [
    re_path(r"^$", views.project_list, name="kg_project_list"),
    re_path(r"^add/$", views.add_edit_project, name="kg_project_add"),
    re_path(r"^no_users/$", views.no_users, name="kg_empty_projects_list"),
    re_path(r"^(?P<project_id>\d+)/$", views.project_detail, name="kg_project_detail"),
    re_path(r"^(?P<project_id>\d+)/verbose/$", views.project_verbose, name="kg_project_verbose"),
    re_path(r"^(?P<project_id>\d+)/edit/$", views.add_edit_project, name="kg_project_edit"),
    re_path(r"^(?P<project_id>\d+)/undelete/$", views.undelete_project, name="kg_project_undelete"),
    re_path(r"^(?P<project_id>\d+)/delete/$", views.delete_project, name="kg_project_delete"),
    re_path(
        r"^(?P<project_id>\d+)/remove_user/(?P<username>%s)/$" % (settings.USERNAME_VALIDATION_RE,),
        views.remove_user,
        name="kg_remove_project_member",
    ),
    re_path(
        r"^(?P<project_id>\d+)/grant/(?P<username>%s)/$" % (settings.USERNAME_VALIDATION_RE,),
        views.grant_leader,
        name="kg_grant_leader",
    ),
    re_path(
        r"^(?P<project_id>\d+)/revoke/(?P<username>%s)/$" % (settings.USERNAME_VALIDATION_RE,),
        views.revoke_leader,
        name="kg_revoke_leader",
    ),
    re_path(r"^(?P<project_id>\d+)/logs/$", views.project_logs, name="kg_project_logs"),
    re_path(r"^(?P<project_id>\d+)/add_comment/$", views.add_comment, name="kg_project_add_comment"),
]

profile_urlpatterns = [
    re_path(r"^projects/$", views.profile_projects, name="kg_profile_projects"),
]
