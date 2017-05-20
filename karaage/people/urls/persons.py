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

from django.conf.urls import url, include
from django.conf import settings

from django.contrib.auth import views as django_views

from karaage.people.forms import SetPasswordForm
from karaage.people.views import persons


urlpatterns = [
    url(r'^$', persons.user_list, name='kg_person_list'),
    url(r'^struggling/$', persons.struggling, name='kg_person_struggling'),
    url(r'^locked/$', persons.locked_list, name='kg_person_locked'),

    url(r'^add/$', persons.add_user, name='kg_person_add'),

    url(r'^detail/(?P<username>%s)/' % settings.USERNAME_VALIDATION_RE,
        include('karaage.people.urls.person_detail')),
]

urlpatterns += [
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        django_views.password_reset_confirm, {
            'set_password_form': SetPasswordForm,
            'template_name': 'karaage/people/person_reset_confirm.html',
        }, name='password_reset_confirm'),
    url(r'^reset/done/$',
        django_views.password_reset_complete, {
            'template_name': 'karaage/people/person_reset_complete.html',
        }, name='password_reset_complete'),
]
