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

from django.contrib import admin
from karaage.people.models import Institute, Person

class InstituteAdmin(admin.ModelAdmin):
    list_display = ('name','delegate','active_delegate', 'gid',)
    search_fields = ['name',]

admin.site.register(Institute, InstituteAdmin)


class PersonAdmin(admin.ModelAdmin):
    list_display = ('username', 'get_full_name','email', 'is_active','last_usage')
    search_fields = ['user__first_name', 'user__last_name','comment','user__username','user__email','mobile', 'position']
    list_filter = ['institute']

admin.site.register(Person, PersonAdmin)
