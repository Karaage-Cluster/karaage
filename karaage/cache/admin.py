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
from models import *


class InstituteCacheAdmin(admin.ModelAdmin):
    list_display = ('institute','date','start','end','cpu_hours','no_jobs')
    list_filter = ['institute', 'start', 'machine_category',]

admin.site.register(InstituteCache, InstituteCacheAdmin)



class ProjectCacheAdmin(admin.ModelAdmin):
    list_filter = ['machine_category',]


admin.site.register(ProjectCache, ProjectCacheAdmin)
admin.site.register(UserCache)
admin.site.register(MachineCache)

