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

