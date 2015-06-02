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

from django.template.loader import render_to_string
from django.conf import settings

from karaage.common.emails import CONTEXT, send_mail


def render_email(name, context):
    context.update(CONTEXT)
    subject = render_to_string(
        ['karaage/emails/%s_subject.txt' % name,
            'kgapplications/emails/%s_subject.txt' % name],
        context).replace('\n', '')
    body = render_to_string(
        ['karaage/emails/%s_body.txt' % name,
            'kgapplications/emails/%s_body.txt' % name],
        context)
    return subject, body


def _send_request_email(context, role, persons, template):
    # if APPROVE_ACCOUNTS_EMAIL and this email to administrator role, use this
    # value instead of emailing individual administrators.
    if role == "administrator" and \
            settings.APPROVE_ACCOUNTS_EMAIL is not None:

        context['receiver'] = None
        context['receiver_text'] = "Administatror"

        to_email = settings.APPROVE_ACCOUNTS_EMAIL
        subject, body = render_email(template, context)

        send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email])
        return

    for person in persons:
        if not person.email:
            continue

        context['receiver'] = person
        context['receiver_text'] = person.get_short_name()

        to_email = person.email
        subject, body = render_email(template, context)

        send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email])


def send_request_email(
        authorised_text, authorised_role, authorised_persons, application,
        link, is_secret):
    """Sends an email to admin asking to approve user application"""
    context = CONTEXT.copy()
    context['requester'] = application.applicant
    context['link'] = link
    context['is_secret'] = is_secret
    context['application'] = application
    context['authorised_text'] = authorised_text
    _send_request_email(
        context,
        authorised_role, authorised_persons,
        "common_request")


def send_duplicate_email(
        authorised_text, authorised_role, authorised_persons, application,
        link, is_secret):
    """Sends an email to admin to warn application was marked duplicate."""
    context = CONTEXT.copy()
    context['requester'] = application.applicant
    context['link'] = link
    context['is_secret'] = is_secret
    context['application'] = application
    context['authorised_text'] = authorised_text
    _send_request_email(
        context,
        authorised_role, authorised_persons,
        "project_duplicate_applicant")


def send_invite_email(application, link, is_secret):
    """ Sends an email inviting someone to create an account"""

    if not application.applicant.email:
        return

    context = CONTEXT.copy()
    context['receiver'] = application.applicant
    context['application'] = application
    context['link'] = link
    context['is_secret'] = is_secret

    to_email = application.applicant.email
    subject, body = render_email('common_invite', context)

    send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email])


def send_approved_email(
        application, created_person, created_account, link, is_secret):
    """Sends an email informing person application is approved"""
    if not application.applicant.email:
        return

    context = CONTEXT.copy()
    context['receiver'] = application.applicant
    context['application'] = application
    context['created_person'] = created_person
    context['created_account'] = created_account
    context['link'] = link
    context['is_secret'] = is_secret
    subject, body = render_email('common_approved', context)
    to_email = application.applicant.email

    send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email])
