from django.contrib import admin
from models import Project


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('pid','name','leader','is_expertise','is_active',)
    search_fields = ['pid','name', 'leader__user__first_name','leader__user__last_name',]
    list_filter = ['institute','start_date','end_date','machine_category','is_expertise','is_active',]
    date_hierarchy = 'start_date'


admin.site.register(Project, ProjectAdmin)
