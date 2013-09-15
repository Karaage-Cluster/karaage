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

"""
All email sending is done from this module
"""
__author__ = 'Sam Morrison'

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

from karaage.common import log

CONTEXT = {
    'org_email': settings.ACCOUNTS_EMAIL,
    'org_name': settings.ACCOUNTS_ORG_NAME,
    }


def send_mail(subject, message, from_email, recipient_list):
    headers = {
        'Precedence': 'bulk',
        'Auto-Submitted': 'auto-replied',
    }

    email = EmailMessage(subject, message, from_email, recipient_list,
                        headers=headers)
    return email.send()
