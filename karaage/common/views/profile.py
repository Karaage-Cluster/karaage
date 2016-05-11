# Copyright 2014-2015 VPAC
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

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

import karaage.common.saml as saml
from karaage.common.decorators import login_required


@login_required
def profile(request):
    person = request.user
    return render_to_response(
        'karaage/common/profile.html',
        locals(),
        context_instance=RequestContext(request))


def logout(request, username=None):
    from django.contrib.auth import logout
    logout(request)
    if saml.is_saml_session(request):
        url = saml.logout_url(request)
    else:
        url = reverse("index")
        messages.success(request, 'Logout was successful.')
    return HttpResponseRedirect(url)
