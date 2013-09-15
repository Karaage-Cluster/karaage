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

from karaage.common.emails import CONTEXT, send_mail


def send_software_request_email(software_request):
    """Sends an email to ACCOUNTS_EMAIL when user requests restricted software"""
    context = CONTEXT.copy()
    context['requester'] = software_request.person
    context['software'] = software_request.software_license.package

    to_email = settings.ACCOUNTS_EMAIL
    subject = render_to_string('software/softwarerequest_email_subject.txt', context)
    body = render_to_string('software/softwarerequest_email_body.txt', context)

    send_mail(subject.replace('\n', ''), body, settings.ACCOUNTS_EMAIL, [to_email])


def send_software_request_approved_email(software_request):
    """Sends an email to user when software request approved"""
    context = CONTEXT.copy()
    context['receiver'] = software_request.person
    context['software'] = software_request.software_license.package

    to_email = software_request.person.email
    subject = render_to_string('software/softwarerequest_approved_email_subject.txt', context)
    body = render_to_string('software/softwarerequest_approved_email_body.txt', context)

    send_mail(subject.replace('\n', ''), body, settings.ACCOUNTS_EMAIL, [to_email])
