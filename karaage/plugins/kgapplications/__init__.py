# Copyright 2015 VPAC
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

from karaage.plugins import BasePlugin


class plugin(BasePlugin):
    name = "karaage.plugins.kgapplications"
    template_context_processors = (
        "karaage.plugins.kgapplications.context_processor",)

    settings = {
        'ALLOW_REGISTRATIONS': False,
        'ALLOW_NEW_PROJECTS': True,
        'APPROVE_ACCOUNTS_EMAIL': None,
    }

    def ready(self):
        from . import signals  # NOQA


def context_processor(request):
    """ Set context with common variables. """
    from .models import Application
    ctx = {}

    if request.user.is_authenticated():
        person = request.user
        my_applications = Application.objects.get_for_applicant(person)
        requires_attention = Application.objects.requires_attention(request)

        ctx['pending_applications'] = (
            my_applications.count() + requires_attention.count()
        )

    return ctx
