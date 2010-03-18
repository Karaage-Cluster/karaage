from django.contrib import admin
from models import InstituteChunk, ProjectChunk


#class InstituteChunkAdmin(admin.ModelAdmin):
admin.site.register(InstituteChunk)


#class ProjectChunkAdmin(admin.ModelAdmin):

admin.site.register(ProjectChunk)
