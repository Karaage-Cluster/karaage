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
from django.core.urlresolvers import reverse, get_script_prefix

CONTEXT = {
    'org_email': settings.ACCOUNTS_EMAIL,
    'org_name': settings.ACCOUNTS_ORG_NAME,
    }

TEMPLATE_DIRS = ['emails/', 'applications/emails/']

def render_email(name, context):
    context.update(CONTEXT)
    subject = render_to_string(['emails/%s_subject.txt' % name, 'applications/emails/%s_subject.txt' % name], context).replace('\n','')
    body = render_to_string(['emails/%s_body.txt' % name, 'applications/emails/%s_body.txt' % name], context)
    return subject, body

def remove_url_prefix(url):
    if get_script_prefix() != '/':
        return url.replace(get_script_prefix(), '/', 1)
    return url


def send_notify_admin(application, leader=None):
    """Sends an email to admin asking to approve user application"""
    context = CONTEXT.copy()
    context['requester'] = application.applicant
    context['project'] = application.project
    if leader:
        context['leader'] = leader
    context['site'] = '%s' % remove_url_prefix(reverse('kg_userapplication_detail', args=[application.id]))

    to_email = settings.APPROVE_ACCOUNTS_EMAIL
    subject, body = render_email('notify_admin', context)

    send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)



def send_account_request_email(application):
    """Sends an email to each project leader asking to approve user application"""
    context = CONTEXT.copy()
    context['requester'] = application.applicant
    context['site'] = '%s/applications/%s/' % (settings.REGISTRATION_BASE_URL, application.id)
    context['project'] = application.project

    for leader in application.project.leaders.filter(user__is_active=True):
        context['receiver'] = leader
        
        to_email = leader.email
        subject, body = render_email('join_project_request', context)

        send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)


def send_user_invite_email(userapplication):
    """ Sends an email inviting someone to create an account"""

    context = CONTEXT.copy()
    context['site'] = '%s/applications/%s/do/' % (settings.REGISTRATION_BASE_URL, application.secret_token)
    context['sender'] = userapplication.created_by
    context['project'] = userapplication.project
    context['make_leader'] = userapplication.make_leader
    context['message'] = userapplication.header_message

    to_email = userapplication.applicant.email 
    subject, body = render_email('user_invite', context)
    
    send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)


def send_account_approved_email(userapplication):
    """Sends an email informing person account is ready"""
    context = CONTEXT.copy()
    context['receiver'] = userapplication.applicant
    context['project'] = userapplication.project
    context['site'] = '%s/profile/' % settings.REGISTRATION_BASE_URL
    subject, body = render_email('account_approved', context)
    to_email = userapplication.applicant.email
    
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


def send_project_request_email(application):
    """Sends an email to the projects institutes active delegate for approval"""
    context = CONTEXT.copy()
    context['requester'] = application.applicant
    context['site'] = '%s/applications/projects/%s/' % (settings.REGISTRATION_BASE_URL, application.id)
    context['application'] = application 

    for delegate in application.institute.delegates.filter(institutedelegate__send_email=True):
        context['receiver'] = delegate
        to_email = delegate.email
        subject, body = render_email('project_request', context)
        send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)


def send_project_approved_email(application):
    """Sends an email to the projects leaders once approved"""
    context = CONTEXT.copy()
    context['site'] = '%s/projects/%s/' % (settings.REGISTRATION_BASE_URL, application.project.pid)
    context['project'] = application.project 
 
    for leader in application.project.leaders.all():
        context['receiver'] =  leader
        subject, body = render_email('project_approved', context)
        to_email = leader.email
        send_mail(subject, body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)
        
