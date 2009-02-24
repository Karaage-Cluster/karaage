from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required, login_required
from django.core.mail import send_mass_mail
from django.core.urlresolvers import reverse

from karaage.emails.forms import EmailForm

@login_required
def send_email(request):

    if request.method == 'POST':
        
        form = EmailForm(request.POST)
            
        if form.is_valid():

            if 'preview' in request.POST:
                emails = form.get_emails()
                try:
                    preview = emails[0]
                except:
                    pass
            else:
            
                send_mass_mail(form.get_emails())
                request.user.message_set.create(message="Emails sent successfully")
                    
                return HttpResponseRedirect(reverse('kg_admin_index'))
            
    else:
        
        form = EmailForm()
        
    return render_to_response('emails/send_email_form.html', locals(), context_instance=RequestContext(request))


send_email = permission_required('emails.send_email')(send_email)
