from django.contrib import admin
from models import *


admin.site.register(SoftwareCategory)
admin.site.register(SoftwarePackage)
admin.site.register(SoftwareVersion)
admin.site.register(SoftwareLicense)

class SoftwareLicenseAgreementAdmin(admin.ModelAdmin):
    list_display = ('user', 'license', 'date', )

admin.site.register(SoftwareLicenseAgreement, SoftwareLicenseAgreementAdmin)
