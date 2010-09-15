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
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.contrib import messages

import datetime

from karaage.applications.models import UserApplication
from karaage.applications.forms import UserApplicationForm


def do_userapplication(request, token):

    application = get_object_or_404(UserApplication, secret_token=token)

    if request.method == 'POST':
        form = UserApplicationForm(request.POST, instance=application)

        if form.is_valid():
            application = form.save()
            application.submitted_date = datetime.datetime.now()
            application.save()
            return HttpResponseRedirect('')
        

    else:
        form = UserApplicationForm(instance=application)
    
    return render_to_response('applications/userapplication_form.html', {'form': form, 'application': application}, context_instance=RequestContext(request)) 
