"""
All email sending is done from this module
"""
__author__ = 'Sam Morrison'

from django.core.mail import send_mail, send_mass_mail
from django.contrib.sites.models import Site
from django.template import Context, Template
from django.conf import settings
from django.db import connection
from django.core.urlresolvers import reverse
from django.template.defaultfilters import dictsortreversed

from django_common.middleware.threadlocals import get_current_user
import datetime

from karaage.projects.models import Project
from karaage.machines.models import MachineCategory, UserAccount

from karaage.emails.models import EmailTemplate
from karaage.util import log_object as log

# Not good should be id=settings.SITE_ID
#TODO
#site = Site.objects.get(name='user')
site = Site.objects.get_current()


def send_account_request_email(user_request):
    """Sends an email to project leader asking to approve person"""
    
    email = EmailTemplate.objects.get(name='account_request')

    c = Context({
        'requester': user_request.person,
        'receiver':  user_request.project.leader,
        'site': '%s%s' % (site.domain, reverse('user_account_request_detail', args=[user_request.id])),
        'project': user_request.project,
        })
    t = Template(email.body)
    to_email = user_request.project.leader.email
    
    send_mail(email.subject, t.render(c), settings.ACCOUNTS_EMAIL_FROM, [to_email], fail_silently=False)


def send_project_request_email(project_request):
    """Sends an email to the projects institutes active delegate for approval"""
    
    email = EmailTemplate.objects.get(name='project_request')

    c = Context({
        'requester': project_request.project.leader,
        'receiver':  project_request.project.institute.active_delegate,
        'site': '%s%s' % (site.domain, reverse('user_project_request_detail', args=[project_request.id])),
        'project': project_request.project,
        })
    t = Template(email.body)
    
    to_email = project_request.project.institute.active_delegate.email
   
    send_mail(email.subject, t.render(c), settings.ACCOUNTS_EMAIL_FROM, [to_email], fail_silently=False)


def send_project_approved_email(project_request):
    """ Sends an email if project has been approved"""

    email = EmailTemplate.objects.get(name='project_approved')

    c = Context({
        'receiver':  project_request.project.leader,
        'site': '%s%s' % (site.domain, reverse('kg_user_profile')),
        'project': project_request.project,
        })
    t = Template(email.body)
    
    to_email = project_request.project.leader.email
   
    send_mail(email.subject, t.render(c), settings.ACCOUNTS_EMAIL_FROM, [to_email], fail_silently=False)


def send_project_rejected_email(project_request):
    """ Sends email if project has been rejected"""

    email = EmailTemplate.objects.get(name='project_rejected')

    c = Context({
        'receiver':  project_request.project.leader,
        'site': '%s%s' % (site.domain, reverse('kg_user_profile')),
        'project': project_request.project,
        })
    t = Template(email.body)
    
    to_email = project_request.project.leader.email

    send_mail(email.subject, t.render(c), settings.ACCOUNTS_EMAIL_FROM, [to_email], fail_silently=False)


def send_account_approved_email(user_request):
    """Sends an email informing person account is ready"""

    email = EmailTemplate.objects.get(name='account_approved')

    c = Context({
        'receiver':  user_request.person,
        'project': user_request.project,
        'site': '%s%s' % (site.domain, reverse('kg_user_profile')),
        })
    t = Template(email.body)
    
    to_email = user_request.person.email
    
    send_mail(email.subject, t.render(c), settings.ACCOUNTS_EMAIL_FROM, [to_email], fail_silently=False)


def send_account_rejected_email(user_request):
    """Sends an email informing person account has been rejected"""

    email = EmailTemplate.objects.get(name='account_rejected')

    c = Context({
        'receiver':  user_request.person,
        'project': user_request.project,
        'site': '%s%s' % (site.domain, reverse('kg_user_profile')),
        })
    t = Template(email.body)
    
    to_email = user_request.person.email
    
    send_mail(email.subject, t.render(c), settings.ACCOUNTS_EMAIL_FROM, [to_email], fail_silently=False)
    

def send_project_join_approved_email(user_request):
    """Sends an email informing person request to join project approved"""

    email = EmailTemplate.objects.get(name='project_joined_approved')

    c = Context({
        'project': user_request.project,
        'receiver':  user_request.person,
        'site': '%s%s' % (site.domain, reverse('kg_user_profile')),
        })
    t = Template(email.body)
    
    to_email = user_request.person.email
    
    send_mail(email.subject, t.render(c), settings.ACCOUNTS_EMAIL_FROM, [to_email], fail_silently=False)
    

def send_removed_from_project_email(person, project):
    """Sends an email informing person they have been removed from project"""

    email = EmailTemplate.objects.get(name='removed_from_project')

    c = Context({
        'project': project,
        'receiver':  person,
        'site': '%s%s' % (site.domain, reverse('kg_user_profile')),
        })
    t = Template(email.body)
    
    to_email = person.email
    
    send_mail(email.subject, t.render(c), settings.ACCOUNTS_EMAIL_FROM, [to_email], fail_silently=False)
    

def send_bounced_warning(person):
    """Sends an email to each project leader for person
    informing them that person's email has bounced"""

    email = EmailTemplate.objects.get(name='bounced_email')
    body_t = Template(email.body)
    subject_t = Template(email.subject)
    for p in person.project_set.all():
        if p.is_active:
            
            c = Context({
                'project': p,
                'receiver':  p.leader,
                'person': person,
                })
    
            to_email = p.leader.email
    
            send_mail(subject_t.render(c), body_t.render(c), settings.ACCOUNTS_EMAIL_FROM, [to_email], fail_silently=False)
            active_user = get_current_user()
            
            log(active_user, p.leader, 2, 'Sent email about bounced emails from %s' % person)


def send_leader_quarter_summary_emails():
    """Sends an email informing person request to join project approved"""

    email = EmailTemplate.objects.get(name='leader_quarter_summary')
    body_t = Template(email.body)
    subject_t = Template(email.subject)

    email_list = []

    end = datetime.date.today()
    start = end - datetime.timedelta(days=90)

    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    machine_category = MachineCategory.objects.get_default()
    mc_ids = tuple([(int(m.id)) for m in machine_category.machine_set.all()])
    if len(mc_ids) == 1:
        mc_ids = "(%i)" % mc_ids[0]

    for p in Project.active.filter(pid='VPAC_Sys'):
        
        usage_list = []
        total, total_jobs = 0, 0

        cursor = connection.cursor()
        SQL = "SELECT user_id from cpu_job where project_id = '%s' and `machine_id` IN %s AND `date` >= '%s' AND `date` <= '%s' GROUP BY user_id" % (str(p.pid), mc_ids, start_str, end_str)
        cursor.execute(SQL)
        rows = list(cursor.fetchall())
        cursor.close()

        for uid in rows:
            u = UserAccount.objects.get(id=uid[0]).user
            time, jobs = u.get_usage(p, start, end)
            total += time
            total_jobs += jobs
            if jobs > 0:
                usage_list.append({ 'user': u, 'usage': time, 'jobs': jobs,})
    
        usage_list = dictsortreversed(usage_list, 'usage')


        c = Context({
                'project': p,
                'receiver':  p.leader,
                'members': p.users.all(),
                'usage_list': usage_list,
                #'project_users_site': '%s/%sprofile/project_users/' % (site.domain, settings.BASE_URL),
                'usage_site': p.get_usage_url(),
                'start': start,
                'end': end,
                'site': '%s%s%s' % (site.domain, settings.BASE_URL, reverse('kg_user_profile')),
                })
    
        #to_email = p.leader.email
        to_email = 'sam@vpac.org'
    
#        send_mail(subject_t.render(c), body_t.render(c), settings.ACCOUNTS_EMAIL_FROM, [to_email], fail_silently=False)
    
        body = body_t.render(c)
        print body
        print body.replace('\\t', '\t')

        email_list.append((subject_t.render(c), body, settings.ACCOUNTS_EMAIL_FROM, [to_email]))
        c = 0
    
    
        
#    send_mass_mail(email_list)
