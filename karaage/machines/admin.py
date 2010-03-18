from django.contrib import admin
from models import MachineCategory, Machine, UserAccount

class UserAccountAdmin(admin.ModelAdmin):
    search_fields = ['username',]

admin.site.register(MachineCategory)
admin.site.register(Machine)
admin.site.register(UserAccount, UserAccountAdmin)

