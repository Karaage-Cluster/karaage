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

from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.conf import settings
from django.core.urlresolvers import reverse

from andsome.middleware.threadlocals import get_current_user

from karaage.util import log_object as log


CONTEXT = {
    'org_email': settings.ACCOUNTS_EMAIL,
    'org_name': settings.ACCOUNTS_ORG_NAME,
    }


def send_account_request_email(user_request):
    """Sends an email to each project leader asking to approve person"""
    site = Site.objects.get_current()
    context = CONTEXT.copy()
    context['requester'] = user_request.person
    context['site'] = '%s%s' % (site.domain, reverse('user_account_request_detail', args=[user_request.id]))
    context['project'] = user_request.project

    for leader in user_request.project.leaders.all():
        context['receiver'] = leader
            
        to_email = leader.email        
        subject = render_to_string('requests/emails/join_project_request_subject.txt', context)
        body = render_to_string('requests/emails/join_project_request_body.txt', context)

        send_mail(subject.replace('\n',''), body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)


def send_project_request_email(project_request):
    """Sends an email to the projects institutes active delegate for approval"""
    site = Site.objects.get_current()
    context = CONTEXT.copy()
    context['requester'] = project_request.project.leaders.all()[0]
    context['receiver'] =  project_request.project.institute.active_delegate
    context['site'] = '%s%s' % (site.domain, reverse('user_project_request_detail', args=[project_request.id]))
    context['project'] = project_request.project     

    subject = render_to_string('requests/emails/create_project_request_subject.txt', context)
    body = render_to_string('requests/emails/create_project_request_body.txt', context)

    to_email = project_request.project.institute.active_delegate.email

    send_mail(subject.replace('\n',''), body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)


def send_project_approved_email(project_request):
    """ Sends an email if project has been approved"""
    site = Site.objects.get_current()
    context = CONTEXT.copy()
    context['project'] = project_request.project   
    context['site'] = '%s%s' % (site.domain, reverse('kg_user_profile'))

    for leader in project_request.project.leaders.all():
        context['receiver'] = leader    
        to_email = leader.email
        subject = render_to_string('requests/emails/project_approved_subject.txt', context)
        body = render_to_string('requests/emails/project_approved_body.txt', context)

        send_mail(subject.replace('\n',''), body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)


def send_project_rejected_email(project_request):
    """ Sends email if project has been rejected"""
    site = Site.objects.get_current()
    context = CONTEXT.copy()
    context['project'] = project_request.project 
    context['site'] = '%s%s' % (site.domain, reverse('kg_user_profile'))

    for leader in project_request.project.leaders.all():
        context['receiver'] = leader 
        subject = render_to_string('requests/emails/project_rejected_subject.txt', context)
        body = render_to_string('requests/emails/project_rejected_body.txt', context)
        to_email = leader.email

        send_mail(subject.replace('\n',''), body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)


def send_account_approved_email(user_request):
    """Sends an email informing person account is ready"""
    context = CONTEXT.copy()
    context['receiver'] = user_request.person
    context['project'] = user_request.project
    #context['site'] = '%s%s' % (site.domain, reverse('kg_user_profile'))
        
    subject = render_to_string('requests/emails/account_approved_subject.txt', context)
    body = render_to_string('requests/emails/account_approved_body.txt', context)
    to_email = user_request.person.email
    
    send_mail(subject.replace('\n',''), body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)


def send_account_rejected_email(user_request):
    """Sends an email informing person account has been rejected"""
    context = CONTEXT.copy()
    context['receiver'] = user_request.person
    context['project'] = user_request.project
 
    subject = render_to_string('requests/emails/account_rejected_subject.txt', context)
    body = render_to_string('requests/emails/account_rejected_body.txt', context)  
    to_email = user_request.person.email
    
    send_mail(subject.replace('\n',''), body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)
    

def send_project_join_approved_email(user_request):
    """Sends an email informing person request to join project approved"""
    site = Site.objects.get_current()
    context = CONTEXT.copy()
    context['receiver'] = user_request.person
    context['project'] = user_request.project
    context['site'] = '%s%s' % (site.domain, reverse('kg_user_profile'))

    subject = render_to_string('requests/emails/project_join_approved_subject.txt', context)
    body = render_to_string('requests/emails/project_join_approved_body.txt', context)  
    to_email = user_request.person.email
    
    send_mail(subject.replace('\n',''), body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)


def send_bounced_warning(person):
    """Sends an email to each project leader for person
    informing them that person's email has bounced"""
    context = CONTEXT.copy()
    context['person'] = person

    for project in person.project_set.all():
        if project.is_active:
            context['project'] = project
            for leader in project.leaders.all():
                context['receiver'] =  leader

                to_email = leader.email
                subject = render_to_string('requests/emails/bounced_email_subject.txt', context)
                body = render_to_string('requests/emails/bounced_email_body.txt', context)
                send_mail(subject.replace('\n',''), body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)
                active_user = get_current_user()
                log(active_user, p.leader, 2, 'Sent email about bounced emails from %s' % person)


def send_software_request_email(software_request):
    """Sends an email to ACCOUNTS_EMAIL when user requests restricted software"""
    site = Site.objects.get_current()
    context = CONTEXT.copy()
    context['requester'] = software_request.person
    context['software'] = software_request.software_license.package

    to_email = settings.ACCOUNTS_EMAIL      
    subject = render_to_string('software/softwarerequest_email_subject.txt', context)
    body = render_to_string('software/softwarerequest_email_body.txt', context)

    send_mail(subject.replace('\n',''), body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)
    

def send_software_request_approved_email(software_request):
    """Sends an email to user when software request approved"""
    site = Site.objects.get_current()
    context = CONTEXT.copy()
    context['receiver'] = software_request.person
    context['software'] = software_request.software_license.package

    to_email = software_request.person.email   
    subject = render_to_string('software/softwarerequest_approved_email_subject.txt', context)
    body = render_to_string('software/softwarerequest_approved_email_body.txt', context)

    send_mail(subject.replace('\n',''), body, settings.ACCOUNTS_EMAIL, [to_email], fail_silently=False)
    
