from django.contrib import admin
from models import ProjectJoinRequest, ProjectCreateRequest

class RequestAdmin(admin.ModelAdmin):
    list_display = ('person', 'project', 'date',)
    search_fields = ['person', 'project', 'date']


admin.site.register(ProjectJoinRequest, RequestAdmin)
admin.site.register(ProjectCreateRequest, RequestAdmin)
