# Copyright 2007-2010 VPAC
#
# This file is part of Karaage.
#
# Karaage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Karaage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Karaage  If not, see <http://www.gnu.org/licenses/>.

from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required, login_required
from django.core.mail import send_mass_mail
from django.core.urlresolvers import reverse
from django.contrib import messages

from karaage.emails.forms import EmailForm

@permission_required('emails.send_email')
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
                messages.info(request, "Emails sent successfully")
                    
                return HttpResponseRedirect(reverse('kg_admin_index'))
    else:        
        form = EmailForm()
        
    return render_to_response('emails/send_email_form.html', locals(), context_instance=RequestContext(request))

