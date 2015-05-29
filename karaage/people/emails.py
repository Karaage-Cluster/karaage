# Copyright 2013-2015 VPAC
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

from django.template.loader import render_to_string
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from karaage.common import log
from karaage.common.emails import CONTEXT, send_mail


def render_email(name, context):
    subject = render_to_string(
        ['karaage/emails/%s_subject.txt' % name,
            'karaage/people/emails/%s_subject.txt' % name],
        context)
    subject = subject.replace('\n', '')
    body = render_to_string(
        ['karaage/emails/%s_body.txt' % name,
            'karaage/people/emails/%s_body.txt' % name],
        context)
    return subject, body


def send_bounced_warning(person, leader_list):
    """Sends an email to each project leader for person
    informing them that person's email has bounced"""
    context = CONTEXT.copy()
    context['person'] = person

    for lp in leader_list:
        leader = lp['leader']

        context['project'] = lp['project']
        context['receiver'] = leader

        to_email = leader.email
        subject = render_to_string(
            'karaage/people/emails/bounced_email_subject.txt', context)
        body = render_to_string(
            'karaage/people/emails/bounced_email_body.txt', context)
        send_mail(
            subject.replace('\n', ''), body,
            settings.ACCOUNTS_EMAIL, [to_email])
        log.change(
            leader,
            'Sent email about bounced emails from %s' % person)


def send_reset_password_email(person):
    """Sends an email to user allowing them to set their password."""
    uid = urlsafe_base64_encode(force_bytes(person.pk)).decode("ascii")
    token = default_token_generator.make_token(person)
    url = '%s/persons/reset/%s/%s/' % (
        settings.REGISTRATION_BASE_URL, uid, token)

    context = CONTEXT.copy()
    context.update({
        'url': url,
        'receiver': person,
    })

    to_email = person.email
    subject, body = render_email('reset_password', context)

    send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email])


def send_confirm_password_email(person):
    """Sends an email to user allowing them to confirm their password."""
    url = '%s/profile/login/%s/' % (
        settings.REGISTRATION_BASE_URL, person.username)

    context = CONTEXT.copy()
    context.update({
        'url': url,
        'receiver': person,
    })

    to_email = person.email
    subject, body = render_email('confirm_password', context)

    send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email])
