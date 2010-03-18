from django.contrib.auth import login
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User

class ApacheSiteLogin:
    "This middleware logs a user in using the REMOTE_USER header from apache"
    def process_request(self, request):

        if request.user.is_anonymous():
            try:
                user = User.objects.get(username__exact=request.META['REMOTE_USER'])
                user.backend = 'placard.backends.LDAPBackend'
                login(request, user)
            except:
                return HttpResponseForbidden("<h1>Failed log in.</h1><p>Try to refresh page</p>")










