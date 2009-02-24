from django import forms
from django.conf import settings
from django.template import Context, Template

from karaage.machines.models import MachineCategory
from karaage.people.models import Person
from karaage.projects.models import Project


EMAIL_GROUPS = (
    ('leaders', 'All Project Leaders'),
    ('vpac_users', 'All VPAC Users'),
    #('academic_leaders', 'All VPAC Users (Academic only)'),
    #('academic_users', 'All Project Leaders (Academic only)'),
)


class EmailForm(forms.Form):

    group = forms.ChoiceField(choices=EMAIL_GROUPS)
    subject = forms.CharField(widget=forms.TextInput(attrs={ 'size':60 }))
    body = forms.CharField(widget=forms.Textarea(attrs={'class':'vLargeTextField', 'rows':10, 'cols':40 }))

    def get_emails(self):
        projects, users = None, None
        data = self.cleaned_data
        group = data['group']
        subject = data['subject']
        body = data['body']

        
        if group == 'leaders':
            projects = Project.active.all()

        elif group == 'vpac_users':
            mc = MachineCategory.objects.get(name='VPAC')
            user_ids = []
            for u in Person.active.all():
                if u.has_account(mc):
                    if u.email:
                        user_ids.append(u.id)
            
            users = Person.objects.filter(id__in=user_ids)

        emails = []

        subject_t = Template(subject)
        body_t = Template(body)
        
        if projects:
            for p in projects:
                if p.leader.email:
                    ctx = Context({
                        'receiver': p.leader,
                        'project': p,
                        })

                    subject = subject_t.render(ctx)
                    body = body_t.render(ctx)
                    emails.append((subject, body, settings.ACCOUNTS_EMAIL_FROM, [p.leader.email]))
                    ctx = 0

        if users:
            for u in users:
                ctx = Context({
                    'receiver': u,
                    })
                subject = subject_t.render(ctx)
                body = body_t.render(ctx)
                emails.append((subject, body, settings.ACCOUNTS_EMAIL_FROM, [u.email]))
                ctx = 0

        return emails
            
