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

from django.template.loader import render_to_string
from django.conf import settings
from django.core.urlresolvers import get_script_prefix

from karaage.common.emails import CONTEXT, send_mail

TEMPLATE_DIRS = ['emails/', 'applications/emails/']


def render_email(name, context):
    context.update(CONTEXT)
    subject = render_to_string(['emails/%s_subject.txt' % name, 'applications/emails/%s_subject.txt' % name], context).replace('\n', '')
    body = render_to_string(['emails/%s_body.txt' % name, 'applications/emails/%s_body.txt' % name], context)
    return subject, body


def send_admin_project_request_email(application):
    """Sends an email to admin asking to approve user application"""
    context = CONTEXT.copy()
    context['requester'] = application.applicant
    context['link'] = '%s/applications/%d/' % (settings.REGISTRATION_BASE_URL, application.pk)
    context['application'] = application

    to_email = settings.APPROVE_ACCOUNTS_EMAIL
    subject, body = render_email('project_request_admin', context)

    send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email])


def send_admin_software_request_email(application):
    """Sends an email to admin asking to approve user application"""
    context = CONTEXT.copy()
    context['requester'] = application.applicant
    context['link'] = '%s/applications/%d/' % (settings.REGISTRATION_BASE_URL, application.pk)
    context['application'] = application

    to_email = settings.APPROVE_ACCOUNTS_EMAIL
    subject, body = render_email('software_request_admin', context)

    send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email])


def send_leader_project_request_email(application):
    """Sends an email to each project leader asking to approve user application"""
    context = CONTEXT.copy()
    context['link'] = '%s/applications/%d/' % (settings.REGISTRATION_BASE_URL, application.pk)
    context['application'] = application

    for leader in application.project.leaders.filter(is_active=True):
        context['receiver'] = leader

        to_email = leader.email
        subject, body = render_email('project_request_leader', context)

        send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email])


def send_delegate_project_request_email(application):
    """Sends an email to the projects institutes active delegate for approval"""
    context = CONTEXT.copy()
    context['link'] = '%s/applications/%d/' % (settings.REGISTRATION_BASE_URL, application.pk)
    context['application'] = application

    for delegate in application.institute.delegates.filter(institutedelegate__send_email=True):
        context['receiver'] = delegate
        to_email = delegate.email
        subject, body = render_email('project_request_delegate', context)
        send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email])


def send_invite_email(application, link, is_secret):
    """ Sends an email inviting someone to create an account"""

    context = CONTEXT.copy()
    context['receiver'] = application.applicant
    context['application'] = application
    context['link'] = link
    context['is_secret'] = is_secret

    to_email = application.applicant.email
    subject, body = render_email('common_invite', context)

    send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email])


def send_project_applicant_approved_email(application, created_person, created_account, link, is_secret):
    """Sends an email informing person account is ready"""
    context = CONTEXT.copy()
    context['receiver'] = application.applicant
    context['application'] = application
    context['created_person'] = created_person
    context['created_account'] = created_account
    context['link'] = link
    context['is_secret'] = is_secret
    subject, body = render_email('project_applicant_approved', context)
    to_email = application.applicant.email

    send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email])


def send_project_approved_email(application):
    """Sends an email to the projects leaders once approved"""
    context = CONTEXT.copy()
    context['project_link'] = '%s/projects/%s/' % (settings.REGISTRATION_BASE_URL, application.project.pid)
    context['application'] = application

    for leader in application.project.leaders.all():
        if leader != application.applicant:
            context['receiver'] = leader
            subject, body = render_email('project_approved', context)
            to_email = leader.email
            send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email])


def send_software_approved_email(application):
    """Sends an email informing person software is ready"""
    context = CONTEXT.copy()
    context['receiver'] = application.applicant
    context['application'] = application
    subject, body = render_email('software_approved', context)
    to_email = application.applicant.email

    send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email])

