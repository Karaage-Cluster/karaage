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

""" This file is for common state or transitions that can be shared. """

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseBadRequest

from karaage.emails.forms import EmailForm
from karaage.people.models import Person

from .. import forms, emails
from . import base


class TransitionOpen(base.Transition):
    """ A transition after application opened. """

    def __init__(self, on_success):
        super(TransitionOpen, self).__init__()
        self._on_success = on_success

    def get_next_state(self, request, application, roles):
        """ Retrieve the next state. """
        application.reopen()
        link, is_secret = base.get_email_link(application)
        emails.send_invite_email(application, link, is_secret)
        messages.success(
            request,
            "Sent an invitation to %s."
            % application.applicant.email)
        return self._on_success


class StateWaitingForApproval(base.State):
    """ We need the somebody to provide approval. """
    name = "Waiting for X"
    authorised_text = "X"
    template_approve = "kgapplications/common_approve.html"
    template_decline = "kgapplications/common_decline.html"

    def get_authorised_persons(self, application):
        raise NotImplementedError()

    def get_approve_form(self, request, application, roles):
        raise NotImplementedError()

    def check_can_approve(self, request, application, roles):
        """ Check the person's authorization. """
        try:
            authorised_persons = self.get_authorised_persons(application)
            authorised_persons.get(pk=request.user.pk)
            return True
        except Person.DoesNotExist:
            return False

    def enter_state(self, request, application):
        """ This is becoming the new current state. """
        authorised_persons = self.get_authorised_persons(application)
        link, is_secret = self.get_request_email_link(application)
        emails.send_request_email(
            self.authorised_text,
            self.authorised_role,
            authorised_persons,
            application,
            link, is_secret)

    def get_request_email_link(self, application):
        link, is_secret = base.get_registration_email_link(application)
        return link, is_secret

    def view(self, request, application, label, roles, actions):
        """ Django view method. """
        if self.check_can_approve(request, application, roles):
            roles.add('can_approve')
        if label == "approve" and 'can_approve' in roles:
            tmp_actions = []
            if 'approve' in actions:
                tmp_actions.append("approve")
            if 'duplicate' in actions:
                tmp_actions.append("duplicate")
            actions = tmp_actions
            application_form = self.get_approve_form(
                request, application, roles)
            form = application_form(request.POST or None, instance=application)
            if request.method == 'POST':
                if 'duplicate' in request.POST:
                    return 'duplicate'
                if form.is_valid():
                    form.save()
                    return "approve"
            return render_to_response(
                self.template_approve,
                {'application': application, 'form': form,
                    'authorised_text': self.authorised_text,
                    'actions': actions, 'roles': roles},
                context_instance=RequestContext(request))
        elif label == "decline" and 'can_approve' in roles:
            actions = ['cancel']
            if request.method == 'POST':
                form = EmailForm(request.POST)
                if form.is_valid():
                    to_email = application.applicant.email
                    subject, body = form.get_data()
                    emails.send_mail(
                        subject, body,
                        settings.ACCOUNTS_EMAIL, [to_email])
                    return "cancel"
            else:
                link, is_secret = base.get_email_link(application)
                subject, body = emails.render_email(
                    'common_declined',
                    {'receiver': application.applicant,
                        'authorised_text': self.authorised_text,
                        'application': application,
                        'link': link, 'is_secret': is_secret})
                initial_data = {'body': body, 'subject': subject}
                form = EmailForm(initial=initial_data)
            return render_to_response(
                self.template_decline,
                {'application': application, 'form': form,
                    'authorised_text': self.authorised_text,
                    'actions': actions, 'roles': roles},
                context_instance=RequestContext(request))
        self.context = {
            'authorised_text': self.authorised_text,
        }
        return super(StateWaitingForApproval, self).view(
            request, application, label, roles, actions)


class TransitionSubmit(base.Transition):
    """ A transition after application submitted. """

    def __init__(self, on_success, on_error):
        super(TransitionSubmit, self).__init__()
        self._on_success = on_success
        self._on_error = on_error

    def get_next_state(self, request, application, roles):
        """ Retrieve the next state. """

        # Check for serious errors in submission.
        # Should only happen in rare circumstances.
        errors = application.check_valid()
        if len(errors) > 0:
            for error in errors:
                messages.error(request, error)
            return self._on_error

        # mark as submitted
        application.submit()

        return self._on_success


class TransitionApprove(base.Transition):
    """ A transition after application fully approved. """

    def __init__(self, on_password_needed, on_password_ok, on_error):
        super(TransitionApprove, self).__init__()
        self._on_password_needed = on_password_needed
        self._on_password_ok = on_password_ok
        self._on_error = on_error

    def get_next_state(self, request, application, roles):
        """ Retrieve the next state. """
        # Check for serious errors in submission.
        # Should only happen in rare circumstances.
        errors = application.check_valid()
        if len(errors) > 0:
            for error in errors:
                messages.error(request, error)
            return self._on_error

        # approve application
        approved_by = request.user
        created_person, created_account = application.approve(approved_by)

        # send email
        application.extend()
        link, is_secret = base.get_email_link(application)
        emails.send_approved_email(
            application, created_person, created_account, link, is_secret)

        if created_person or created_account:
            return self._on_password_needed
        else:
            return self._on_password_ok


class StatePassword(base.State):
    """ This application is completed and processed. """
    name = "Password"

    def view(self, request, application, label, roles, actions):
        """ Django view method. """
        if label is None and 'is_applicant' in roles:
            assert application.content_type.model == 'person'
            if application.applicant.has_usable_password():
                form = forms.PersonVerifyPassword(
                    data=request.POST or None, person=application.applicant)
                form_type = "verify"
            else:
                form = forms.PersonSetPassword(
                    data=request.POST or None, person=application.applicant)
                form_type = "set"
            if request.method == 'POST':
                if 'cancel' in request.POST:
                    return 'cancel'
                if form.is_valid():
                    form.save()
                    messages.success(
                        request, 'Password updated. New accounts activated.')
                    for action in actions:
                        if action in request.POST:
                            return action
                    return HttpResponseBadRequest("<h1>Bad Request</h1>")
            return render_to_response(
                'kgapplications/common_password.html',
                {'application': application, 'form': form,
                    'actions': actions, 'roles': roles, 'type': form_type},
                context_instance=RequestContext(request))
        return super(StatePassword, self).view(
            request, application, label, roles, actions)


class StateCompleted(base.State):
    """ This application is completed and processed. """
    name = "Completed"


class StateDeclined(base.State):
    """ This application declined. """
    name = "Declined"

    def enter_state(self, request, application):
        """ This is becoming the new current state. """
        application.decline()

    def view(self, request, application, label, roles, actions):
        """ Django view method. """
        if label is None and \
                'is_applicant' in roles and 'is_admin' not in roles:
            # applicant, admin, leader can reopen an application
            if 'reopen' in request.POST:
                return 'reopen'
            return render_to_response(
                'kgapplications/common_declined.html',
                {'application': application,
                    'actions': actions, 'roles': roles},
                context_instance=RequestContext(request))
        return super(StateDeclined, self).view(
            request, application, label, roles, actions)
