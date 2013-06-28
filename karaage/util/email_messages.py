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

"""
All email sending is done from this module
"""
__author__ = 'Sam Morrison'

from django.core.mail import EmailMessage
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.conf import settings

from karaage.util import log_object as log

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


def send_bounced_warning(person):
    """Sends an email to each project leader for person
    informing them that person's email has bounced"""
    context = CONTEXT.copy()
    context['person'] = person

    for project in person.project_set.all():
        if project.is_active:
            context['project'] = project
            for leader in project.leaders.all():
                context['receiver'] = leader

                to_email = leader.email
                subject = render_to_string('requests/emails/bounced_email_subject.txt', context)
                body = render_to_string('requests/emails/bounced_email_body.txt', context)
                send_mail(subject.replace('\n', ''), body, settings.ACCOUNTS_EMAIL, [to_email])
                log(None, leader, 2, 'Sent email about bounced emails from %s' % person)


def send_software_request_email(software_request):
    """Sends an email to ACCOUNTS_EMAIL when user requests restricted software"""
    site = Site.objects.get_current()
    context = CONTEXT.copy()
    context['requester'] = software_request.person
    context['software'] = software_request.software_license.package

    to_email = settings.ACCOUNTS_EMAIL
    subject = render_to_string('software/softwarerequest_email_subject.txt', context)
    body = render_to_string('software/softwarerequest_email_body.txt', context)

    send_mail(subject.replace('\n', ''), body, settings.ACCOUNTS_EMAIL, [to_email])
    

def send_software_request_approved_email(software_request):
    """Sends an email to user when software request approved"""
    site = Site.objects.get_current()
    context = CONTEXT.copy()
    context['receiver'] = software_request.person
    context['software'] = software_request.software_license.package

    to_email = software_request.person.email
    subject = render_to_string('software/softwarerequest_approved_email_subject.txt', context)
    body = render_to_string('software/softwarerequest_approved_email_body.txt', context)

    send_mail(subject.replace('\n', ''), body, settings.ACCOUNTS_EMAIL, [to_email])
