from django.contrib import admin
from models import Institute, Person

from django.contrib.contenttypes.models import ContentType

admin.site.register(ContentType)

class InstituteAdmin(admin.ModelAdmin):
    list_display = ('name','delegate','active_delegate', 'gid',)
    search_fields = ['name',]

admin.site.register(Institute, InstituteAdmin)


class PersonAdmin(admin.ModelAdmin):
    list_display = ('username', 'get_full_name','email', 'is_active','last_usage')
    search_fields = ['user__first_name', 'user__last_name','comment','user__username','user__email','mobile', 'position']
    list_filter = ['institute']

admin.site.register(Person, PersonAdmin)
