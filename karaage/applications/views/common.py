# Copyright 2007-2013 VPAC
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

""" This file is for common state or transitions that can be shared. """

from django.contrib import messages

import karaage.applications.views.base as base
import karaage.applications.emails as emails


class TransitionOpen(base.Transition):
    """ A transition after application opened. """
    def __init__(self, on_success):
        super(TransitionOpen, self).__init__()
        self._on_success = on_success

    def get_next_state(self, request, application, auth):
        """ Retrieve the next state. """
        application.reopen()
        link, is_secret = base.get_email_link(application)
        emails.send_invite_email(application, link, is_secret)
        messages.success(
                request,
                "Sent an invitation to %s." %
                (application.applicant.email))
        return self._on_success


