from django.contrib import admin
from models import *

class EmailTemplateAdmin(admin.ModelAdmin):
    pass

admin.site.register(EmailTemplate, EmailTemplateAdmin)
