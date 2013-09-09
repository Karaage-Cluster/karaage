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

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

CONTEXT = {
    'org_email': settings.ACCOUNTS_EMAIL,
    'org_name': settings.ACCOUNTS_ORG_NAME,
    }


def render_email(name, context):
    subject = render_to_string(['emails/%s_subject.txt' % name, 'people/emails/%s_subject.txt' % name], context).replace('\n', '')
    body = render_to_string(['emails/%s_body.txt' % name, 'people/emails/%s_body.txt' % name], context)
    return subject, body


def send_reset_password_email(person):
    """Sends an email to user allowing them to set their password."""
    context = CONTEXT.copy()
    context.update({
        'url': person.get_password_reset_url(),
        'receiver': person,
    })

    to_email = person.email
    subject, body = render_email('reset_password', context)

    send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)

def send_confirm_password_email(person):
    """Sends an email to user allowing them to confirm their password."""

    context = CONTEXT.copy()
    context.update({
        'url': '%s/users/%s/login/' % (settings.REGISTRATION_BASE_URL, person.username),
        'receiver': person,
    })

    to_email = person.email
    subject, body = render_email('confirm_password', context)

    send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)
