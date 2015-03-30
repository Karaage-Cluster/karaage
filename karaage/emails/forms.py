# Copyright 2009-2015 VPAC
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

from django import forms
from django.conf import settings
from django.template import Context, Template

from karaage.people.models import Person
from karaage.projects.models import Project


EMAIL_GROUPS = (
    ('leaders', 'All Project Leaders (active projects only)'),
    ('users', 'All Active Users'),
    ('cluster_users', 'All Users with cluster accounts'),
)


class EmailForm(forms.Form):
    subject = forms.CharField(widget=forms.TextInput(attrs={'size': 60}))
    body = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'vLargeTextField', 'rows': 10, 'cols': 40}))

    def get_data(self):
        return self.cleaned_data['subject'], self.cleaned_data['body']


class BulkEmailForm(EmailForm):
    group = forms.ChoiceField(choices=EMAIL_GROUPS)

    def get_emails(self):
        group = self.cleaned_data['group']
        subject, body = self.get_data()

        email_list = []

        subject_t = Template(subject)
        body_t = Template(body)
        emails = []

        if group == 'leaders':
            for p in Project.active.all():
                for leader in p.leaders.all():
                    ctx = Context({
                        'receiver': leader,
                        'project': p,
                    })
                    subject = subject_t.render(ctx)
                    body = body_t.render(ctx)
                    emails.append(
                        (subject, body, settings.ACCOUNTS_EMAIL,
                            [leader.email])
                    )
            return emails

        elif group == 'users':
            person_list = Person.active.all()

        elif group == 'cluster_users':
            person_list = Person.active.filter(account__isnull=False)

        else:
            person_list = None

        if person_list:
            for person in person_list:
                if person.email not in email_list:
                    ctx = Context({
                        'receiver': person,
                    })
                    subject = subject_t.render(ctx)
                    body = body_t.render(ctx)
                    emails.append(
                        (subject, body, settings.ACCOUNTS_EMAIL,
                            [person.email])
                    )
                    email_list.append(person.email)

            return emails

        return []
