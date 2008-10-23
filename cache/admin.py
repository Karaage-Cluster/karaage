from django.contrib import admin
from models import *


class InstituteCacheAdmin(admin.ModelAdmin):
    list_display = ('institute','date','start','end','cpu_hours','no_jobs')
    list_filter = ['institute', 'start',]

admin.site.register(InstituteCache, InstituteCacheAdmin)



class UsageCacheAdmin(admin.ModelAdmin):
    pass


admin.site.register(ProjectCache, UsageCacheAdmin)
admin.site.register(UserCache, UsageCacheAdmin)

