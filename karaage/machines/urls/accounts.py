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

from karaage.machines.views import accounts


urlpatterns = [
    re_path(r"^add/(?P<username>%s)/$" % settings.USERNAME_VALIDATION_RE, accounts.add_account, name="kg_account_add"),
    re_path(
        r"^add_project/(?P<username>%s)/$" % settings.USERNAME_VALIDATION_RE,
        accounts.add_project,
        name="kg_account_add_project",
    ),
    re_path(r"^(?P<account_id>\d+)/$", accounts.account_detail, name="kg_account_detail"),
    re_path(r"^(?P<account_id>\d+)/edit/$", accounts.edit_account, name="kg_account_edit"),
    re_path(r"^(?P<account_id>\d+)/delete/$", accounts.delete_account, name="kg_account_delete"),
    re_path(
        r"^(?P<account_id>\d+)/makedefault/(?P<project_id>%s)/$" % settings.PROJECT_VALIDATION_RE,
        accounts.make_default,
        name="kg_account_set_default",
    ),
    re_path(r"^no_project/$", accounts.no_project_list, name="kg_account_no_project"),
    re_path(r"^no_default/$", accounts.no_default_list, name="kg_account_no_default"),
    re_path(r"^wrong_default/$", accounts.wrong_default_list, name="kg_account_wrong_default"),
    re_path(r"^no_account/$", accounts.no_account_list, name="kg_account_no_account"),
]
