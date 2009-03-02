from django.conf import settings

import socket

from karaage.requests.models import ProjectJoinRequest

def common(request):
    ctx = {}
    #if 'REMOTE_USER' in request.META:
    #    ctx['REMOTE_USER'] = request.META['REMOTE_USER']
    #ctx['meta'] = request.META.items()
    ctx['admin_url'] = settings.ADMIN_MEDIA_PREFIX
    ctx['request_count'] = ProjectJoinRequest.objects.filter(leader_approved=True).count()
    return ctx
