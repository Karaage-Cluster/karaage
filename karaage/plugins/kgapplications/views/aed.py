import json

import six
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
)
from django.shortcuts import render

from karaage.common import log, saml
from karaage.institutes.models import Institute
from karaage.people.models import Person
from karaage.plugins.kgapplications import forms
from karaage.plugins.kgapplications.models import Applicant
from karaage.plugins.kgapplications.views import base
from karaage.plugins.kgapplications.views.states import StateWithSteps, Step
from karaage.projects.models import Project


def _get_applicant_from_saml(request):
    attrs, _ = saml.parse_attributes(request)
    saml_id = attrs['persistent_id']
    try:
        return Person.objects.get(saml_id=saml_id)
    except Person.DoesNotExist:
        pass

    try:
        return Applicant.objects.get(saml_id=saml_id)
    except Applicant.DoesNotExist:
        pass

    return None


class StateStepShibboleth(Step):

    """ Invitation has been sent to applicant. """
    name = "Invitation sent"

    def view(self, request, application, label, roles, actions):
        """ Django view method. """
        status = None
        applicant = application.applicant
        attrs = []

        saml_session = saml.is_saml_session(request)

        # certain actions are supported regardless of what else happens
        if 'cancel' in request.POST:
            return "cancel"
        if 'prev' in request.POST:
            return 'prev'

        # test for conditions where shibboleth registration not required
        if applicant.saml_id is not None:
            status = "You have already registered a shibboleth id."
            form = None
            done = True

        elif application.content_type.model != 'applicant':
            status = "You are already registered in the system."
            form = None
            done = True

        elif (applicant.institute is not None and
                applicant.institute.saml_entityid is None):
            status = "Your institute does not have shibboleth registered."
            form = None
            done = True

        elif Institute.objects.filter(
                saml_entityid__isnull=False).count() == 0:
            status = "No institutes support shibboleth here."
            form = None
            done = True

        else:
            # shibboleth registration is required

            # Do construct the form
            form = saml.SAMLInstituteForm(
                request.POST or None,
                initial={'institute': applicant.institute})
            done = False
            status = None

            # Was it a POST request?
            if request.method == 'POST':

                # Did the login form get posted?
                if 'login' in request.POST and form.is_valid():
                    institute = form.cleaned_data['institute']
                    applicant.institute = institute
                    applicant.save()
                    # We do not set application.insitute here, that happens
                    # when application, if it is a ProjectApplication, is
                    # submitted

                    # if institute supports shibboleth, redirect back here via
                    # shibboleth, otherwise redirect directly back he.
                    url = base.get_url(request, application, roles, label)
                    if institute.saml_entityid is not None:
                        url = saml.build_shib_url(
                            request, url, institute.saml_entityid)
                    return HttpResponseRedirect(url)

                # Did we get a logout request?
                elif 'logout' in request.POST:
                    if saml_session:
                        url = saml.logout_url(request)
                        return HttpResponseRedirect(url)
                    else:
                        return HttpResponseBadRequest("<h1>Bad Request</h1>")

            # did we get a shib session yet?
            if saml_session:
                attrs, _ = saml.parse_attributes(request)
                saml_session = True

        # if we are done, we can proceed to next state
        if request.method == 'POST':
            if 'cancel' in request.POST:
                return "cancel"
            if 'prev' in request.POST:
                return 'prev'

            if not done:
                if saml_session:
                    applicant = _get_applicant_from_saml(request)
                    if applicant is not None:
                        application.applicant = applicant
                        application.save()
                    else:
                        applicant = application.applicant

                    applicant = saml.add_saml_data(
                        applicant, request)
                    applicant.save()

                    done = True
                else:
                    status = "Please login to SAML before proceeding."

        if request.method == 'POST' and done:
            for action in actions:
                if action in request.POST:
                    return action
            return HttpResponseBadRequest("<h1>Bad Request</h1>")

        # render the page
        return render(
            template_name='kgapplications/project_aed_shibboleth.html',
            context={
                'form': form,
                'done': done,
                'status': status,
                'actions': actions,
                'roles': roles,
                'application': application,
                'attrs': attrs,
                'saml_session': saml_session,
            },
            request=request)


class StateStepApplicant(Step):

    """ Application is open and user is can edit it."""
    name = "Open"

    def view(self, request, application, label, roles, actions):
        """ Django view method. """
        # Get the appropriate form
        status = None
        form = None

        if application.content_type.model != 'applicant':
            status = "You are already registered in the system."
        elif application.content_type.model == 'applicant':
            if application.applicant.saml_id is not None:
                form = forms.SAMLApplicantForm(
                    request.POST or None,
                    instance=application.applicant)
            else:
                form = forms.UserApplicantForm(
                    request.POST or None,
                    instance=application.applicant)

        # Process the form, if there is one
        if form is not None and request.method == 'POST':
            if form.is_valid():
                form.save(commit=True)
                for action in actions:
                    if action in request.POST:
                        return action
                return HttpResponseBadRequest("<h1>Bad Request</h1>")
            else:
                # if form didn't validate and we want to go back or cancel,
                # then just do it.
                if 'cancel' in request.POST:
                    return "cancel"
                if 'prev' in request.POST:
                    return 'prev'

        # If we don't have a form, we can just process the actions here
        if form is None:
            for action in actions:
                if action in request.POST:
                    return action

        # Render the response
        return render(
            template_name='kgapplications/project_aed_applicant.html',
            context={
                'form': form,
                'application': application,
                'status': status, 'actions': actions, 'roles': roles,
            },
            request=request)


class StateStepProject(Step):

    """ Applicant is able to choose the project for the application. """
    name = "Choose project"

    def handle_ajax(self, request, application):
        resp = {}
        if 'leader' in request.POST:
            leader = Person.objects.get(pk=request.POST['leader'])
            project_list = leader.leads.filter(is_active=True)
            resp['project_list'] = \
                [(p.pk, six.text_type(p)) for p in project_list]

        elif 'terms' in request.POST:
            terms = request.POST['terms'].lower()
            try:
                project = Project.active.get(pid__icontains=terms)
                resp['project_list'] = [(project.pk, six.text_type(project))]
            except Project.DoesNotExist:
                resp['project_list'] = []
            except Project.MultipleObjectsReturned:
                resp['project_list'] = []
            leader_list = Person.active.filter(
                institute=application.applicant.institute,
                leads__is_active=True).distinct()
            if len(terms) >= 3:
                query = Q()
                for term in terms.split(' '):
                    q = Q(username__icontains=term)
                    q = q | Q(short_name__icontains=term)
                    q = q | Q(full_name__icontains=term)
                    query = query & q
                leader_list = leader_list.filter(query)
                resp['leader_list'] = [
                    (p.pk, "%s (%s)" % (p, p.username)) for p in leader_list]
            else:
                resp['error'] = "Please enter at lease three " \
                    "characters for search."
                resp['leader_list'] = []

        return resp

    def view(self, request, application, label, roles, actions):
        """ Django view method. """
        if 'ajax' in request.POST:
            resp = self.handle_ajax(request, application)
            return HttpResponse(
                json.dumps(resp), content_type="application/json")

        form_models = {
            'common': forms.CommonApplicationForm,
            'new': forms.NewProjectApplicationForm,
            'existing': forms.ExistingProjectApplicationForm,
        }

        project_forms = {}

        for key, form in six.iteritems(form_models):
            project_forms[key] = form(
                request.POST or None, instance=application)

        if application.project is not None:
            project_forms["common"].initial = {'application_type': 'U'}
        elif application.name != "":
            project_forms["common"].initial = {'application_type': 'P'}

        if 'application_type' in request.POST:
            at = request.POST['application_type']
            valid = True
            if at == 'U':
                # existing project
                if project_forms['common'].is_valid():
                    project_forms['common'].save(commit=False)
                else:
                    valid = False
                if project_forms['existing'].is_valid():
                    project_forms['existing'].save(commit=False)
                else:
                    valid = False

            elif at == 'P':
                # new project
                if project_forms['common'].is_valid():
                    project_forms['common'].save(commit=False)
                else:
                    valid = False
                if project_forms['new'].is_valid():
                    project_forms['new'].save(commit=False)
                else:
                    valid = False
                application.institute = application.applicant.institute

            else:
                return HttpResponseBadRequest("<h1>Bad Request</h1>")

            # reset hidden forms
            if at != 'U':
                # existing project form was not displayed
                project_forms["existing"] = (
                    form_models["existing"](instance=application))
                application.project = None
            if at != 'P':
                # new project form was not displayed
                project_forms["new"] = form_models["new"](instance=application)
                application.name = ""
                application.institute = None
                application.description = None
                application.additional_req = None
                application.machine_categories = []
                application.pid = None

            # save the values
            application.save()

            if project_forms['new'].is_valid() and at == 'P':
                project_forms["new"].save_m2m()

            # we still need to process cancel and prev even if form were
            # invalid
            if 'cancel' in request.POST:
                return "cancel"
            if 'prev' in request.POST:
                return 'prev'

            # if forms were valid, jump to next state
            if valid:
                for action in actions:
                    if action in request.POST:
                        return action
                return HttpResponseBadRequest("<h1>Bad Request</h1>")
        else:
            # we still need to process cancel, prev even if application type
            # not given
            if 'cancel' in request.POST:
                return "cancel"
            if 'prev' in request.POST:
                return 'prev'

        # lookup the project based on the form data
        project_id = project_forms['existing']['project'].value()
        project = None
        if project_id:
            try:
                project = Project.objects.get(pk=project_id)
            except Project.DoesNotExist:
                pass

        # render the response
        return render(
            template_name='kgapplications/project_aed_project.html',
            context={
                'forms': project_forms,
                'project': project,
                'actions': actions,
                'roles': roles,
                'application': application,
            },
            request=request)


class StateStepIntroduction(Step):

    """ Invitation has been sent to applicant. """
    name = "Read introduction"

    def view(self, request, application, label, roles, actions):
        """ Django get_next_action method. """
        if application.content_type.model == 'applicant':
            if not application.applicant.email_verified:
                application.applicant.email_verified = True
                application.applicant.save()
        for action in actions:
            if action in request.POST:
                return action
        link, is_secret = base.get_email_link(application)
        return render(
            template_name='kgapplications/project_aed_introduction.html',
            context={
                'actions': actions,
                'application': application, 'roles': roles,
                'link': link, 'is_secret': is_secret,
            },
            request=request)


class StateApplicantEnteringDetails(StateWithSteps):
    name = "Applicant entering details."
    actions = {'cancel', 'duplicate', 'reopen', 'submit'}

    def __init__(self, config):
        super(StateApplicantEnteringDetails, self).__init__(config)
        self.add_step(StateStepIntroduction(), 'intro')
        if settings.SHIB_SUPPORTED:
            self.add_step(StateStepShibboleth(), 'shibboleth')
        self.add_step(StateStepApplicant(), 'applicant')
        self.add_step(StateStepProject(), 'project')

    def get_actions(self, request, applications, roles):
        actions = set(self.actions)
        if 'is_applicant' not in roles:
            if 'submit' in actions:
                actions.remove('submit')
        return actions

    def get_next_action(self, request, application, label, roles):
        """ Process the get_next_action request at the current step. """

        # if user is logged and and not applicant, steal the
        # application
        if 'is_applicant' in roles:
            # if we got this far, then we either we are logged in as applicant,
            # or we know the secret for this application.

            new_person = None
            reason = None
            details = None

            attrs, _ = saml.parse_attributes(request)
            saml_id = attrs['persistent_id']
            if saml_id is not None:
                query = Person.objects.filter(saml_id=saml_id)
                if application.content_type.model == "person":
                    query = query.exclude(pk=application.applicant.pk)
                if query.count() > 0:
                    new_person = Person.objects.get(saml_id=saml_id)
                    reason = "SAML id is already in use by existing person."
                    details = (
                        "It is not possible to continue this application " +
                        "as is because the saml identity already exists " +
                        "as a registered user.")
                del query

            if request.user.is_authenticated:
                new_person = request.user
                reason = "%s was logged in " \
                    "and accessed the secret URL." % new_person
                details = (
                    "If you want to access this application " +
                    "as %s " % application.applicant +
                    "without %s stealing it, " % new_person +
                    "you will have to ensure %s is " % new_person +
                    "logged out first.")

            if new_person is not None:
                if application.applicant != new_person:
                    if 'steal' in request.POST:
                        old_applicant = application.applicant
                        application.applicant = new_person
                        application.save()
                        log.change(
                            application.application_ptr,
                            "Stolen application from %s" % old_applicant)
                        messages.success(
                            request,
                            "Stolen application from %s" % old_applicant)
                        url = base.get_url(request, application, roles, label)
                        return HttpResponseRedirect(url)
                    else:
                        return render(
                            template_name='kgapplications'
                            '/project_aed_steal.html',
                            context={
                                'application': application,
                                'person': new_person,
                                'reason': reason,
                                'details': details,
                            },
                            request=request)

        # if the user is the leader, show him the leader specific page.
        if ('is_leader' in roles or 'is_delegate' in roles) \
                and 'is_admin' not in roles \
                and 'is_applicant' not in roles:
            actions = ['reopen']
            if 'reopen' in request.POST:
                return 'reopen'
            return render(
                template_name='kgapplications/project_aed_for_leader.html',
                context={'application': application,
                         'actions': actions, 'roles': roles, },
                request=request)

        # otherwise do the default behaviour for StateWithSteps
        return super(StateApplicantEnteringDetails, self) \
            .get_next_action(request, application, label, roles)
