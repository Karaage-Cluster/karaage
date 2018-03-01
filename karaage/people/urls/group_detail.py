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
from django.conf.urls import url

from karaage.people.views import groups


urlpatterns = [
    url(r'^$', groups.group_detail, name='kg_group_detail'),
    url(r'^verbose/$', groups.group_verbose, name='kg_group_verbose'),
    url(r'^delete/$', groups.delete_group, name='kg_group_delete'),
    url(r'^add/$', groups.add_group_member, name='kg_group_add_person'),
    url(r'^remove/(?P<username>%s)/$' % settings.USERNAME_VALIDATION_RE,
        groups.remove_group_member, name='kg_group_remove_person'),
    url(r'^logs/$', groups.group_logs, name='kg_group_logs'),
    url(r'^add_comment/$', groups.add_comment, name='kg_group_add_comment'),
    url(r'^edit/$', groups.edit_group, name='kg_group_edit'),
]
