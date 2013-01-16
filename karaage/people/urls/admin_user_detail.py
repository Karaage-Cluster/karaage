# Copyright 2007-2010 VPAC
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
from karaage.people.forms import AdminPersonForm

urlpatterns = patterns('karaage.people.views.admin_user_detail',

    url(r'^$', 'user_detail', name='kg_user_detail'),
    url(r'^activate/$', 'activate', name='admin_activate_user'),
    url(r'^jobs/$', 'user_job_list'), 
    url(r'^delete/$', 'delete_user', name='admin_delete_user'),
    url(r'^password_change/$', 'password_change', name='kg_password_change'),
    url(r'^lock/$', 'lock_person', name='kg_lock_user'),
    url(r'^unlock/$', 'unlock_person', name='kg_unlock_user'),
    url(r'^bounced_email/$', 'bounced_email'),
    url(r'^comments/$', 'user_comments', name='kg_user_comments'),
    url(r'^add_comment/$', 'add_comment', name='kg_user_add_comment'),

)

urlpatterns += patterns('karaage.people.views.admin',
    
    url(r'^add_useraccount/$', 'add_edit_useraccount', name='kg_add_useraccount'),
    url(r'^edit/$', 'add_edit_user', {'form_class': AdminPersonForm }, name='kg_user_edit'),
)
