# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
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

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mass_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template import Context, Template
from django.urls import reverse

from karaage.common.decorators import admin_required
from karaage.emails.forms import BulkEmailForm


def _get_emails(person_query, subject, body):
    emails = []

    if person_query:
        email_list = []

        subject_t = Template(subject)
        body_t = Template(body)

        person_query = person_query.filter(is_systemuser=False, login_enabled=True)

        for person in person_query:
            if person.email not in email_list:
                projects = ", ".join([str(project) for project in person.leads.all()])
                ctx = Context(
                    {
                        "projects": projects,
                        "receiver": person,
                    }
                )
                subject = subject_t.render(ctx)
                body = body_t.render(ctx)
                emails.append((subject, body, settings.ACCOUNTS_EMAIL, [person.email]))
                email_list.append(person.email)

    return emails


@admin_required
def send_email(request):

    form = BulkEmailForm(request.POST or None)
    if request.method == "POST":

        if form.is_valid():
            subject = form.cleaned_data["subject"]
            body = form.cleaned_data["body"]
            person_query = form.get_person_query()
            emails = _get_emails(person_query, subject, body)

            if "preview" in request.POST:
                try:
                    preview = emails[0]
                except IndexError:
                    preview = None
            else:
                send_mass_mail(emails)
                messages.success(request, "Emails sent successfully")

                return HttpResponseRedirect(reverse("index"))

    return render(template_name="karaage/emails/send_email_form.html", context=locals(), request=request)
