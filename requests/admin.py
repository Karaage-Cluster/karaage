from django.contrib import admin
from models import UserRequest, ProjectRequest, ProjectJoinRequest, ProjectCreateRequest

admin.site.register(UserRequest)
admin.site.register(ProjectRequest)
admin.site.register(ProjectJoinRequest)
admin.site.register(ProjectCreateRequest)
