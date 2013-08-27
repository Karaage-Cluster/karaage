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

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.core.urlresolvers import get_script_prefix

CONTEXT = {
    'org_email': settings.ACCOUNTS_EMAIL,
    'org_name': settings.ACCOUNTS_ORG_NAME,
    }

TEMPLATE_DIRS = ['emails/', 'applications/emails/']


def render_email(name, context):
    context.update(CONTEXT)
    subject = render_to_string(['emails/%s_subject.txt' % name, 'applications/emails/%s_subject.txt' % name], context).replace('\n', '')
    body = render_to_string(['emails/%s_body.txt' % name, 'applications/emails/%s_body.txt' % name], context)
    return subject, body


def remove_url_prefix(url):
    if get_script_prefix() != '/':
        return url.replace(get_script_prefix(), '/', 1)
    return url


def send_admin_request_email(application):
    """Sends an email to admin asking to approve user application"""
    context = CONTEXT.copy()
    context['requester'] = application.applicant
    context['site'] = '%s/applications/%d/' % (settings.REGISTRATION_BASE_URL, application.pk)
    context['application'] = application

    to_email = settings.APPROVE_ACCOUNTS_EMAIL
    subject, body = render_email('request_admin', context)

    send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)


def send_leader_request_email(application):
    """Sends an email to each project leader asking to approve user application"""
    context = CONTEXT.copy()
    context['site'] = '%s/applications/%d/' % (settings.REGISTRATION_BASE_URL, application.pk)
    context['application'] = application

    for leader in application.project.leaders.filter(user__is_active=True):
        context['receiver'] = leader

        to_email = leader.email
        subject, body = render_email('request_leader', context)

        send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)


def send_delegate_request_email(application):
    """Sends an email to the projects institutes active delegate for approval"""
    context = CONTEXT.copy()
    context['site'] = '%s/applications/%d/' % (settings.REGISTRATION_BASE_URL, application.pk)
    context['application'] = application

    for delegate in application.institute.delegates.filter(institutedelegate__send_email=True):
        context['receiver'] = delegate
        to_email = delegate.email
        subject, body = render_email('request_delegate', context)
        send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)



def send_user_invite_email(application):
    """ Sends an email inviting someone to create an account"""

    context = CONTEXT.copy()
    context['receiver'] = application.applicant
    context['site'] = '%s/applications/%s/' % (settings.REGISTRATION_BASE_URL, application.secret_token)
    context['application'] = application

    to_email = application.applicant.email
    subject, body = render_email('user_invite', context)

    send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)


def send_account_approved_email(application, created_person, created_account, link):
    """Sends an email informing person account is ready"""
    context = CONTEXT.copy()
    context['receiver'] = application.applicant
    context['application'] = application
    context['site'] = '%s/profile/' % settings.REGISTRATION_BASE_URL
    context['created_person'] = created_person
    context['created_account'] = created_account
    context['link'] = link
    subject, body = render_email('account_approved', context)
    to_email = application.applicant.email

    send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)


def send_account_declined_email(userapplication):
    """Sends an email informing person account is declined"""
    context = CONTEXT.copy()
    context['receiver'] = userapplication.applicant
    context['project'] = userapplication.project
    context['site'] = '%s/profile/' % settings.REGISTRATION_BASE_URL
    subject, body = render_email('account_declined', context)
    to_email = userapplication.applicant.email

    send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)


def send_project_approved_email(application):
    """Sends an email to the projects leaders once approved"""
    context = CONTEXT.copy()
    context['site'] = '%s/projects/%s/' % (settings.REGISTRATION_BASE_URL, application.project.pid)
    context['application'] = application

    for leader in application.project.leaders.all():
        if leader != application.applicant:
            context['receiver'] = leader
            subject, body = render_email('project_approved', context)
            to_email = leader.email
            send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)
