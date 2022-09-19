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

import ajax_select.fields
import six
from captcha.fields import CaptchaField
from django import forms
from django.conf import settings
from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe

from karaage.common.forms import (
    clean_email,
    validate_password,
    validate_phone_number,
)
from karaage.institutes.models import Institute
from karaage.people.models import Person
from karaage.people.utils import (
    UsernameException,
    validate_username_for_new_person,
)
from karaage.projects.models import Project

from .models import Applicant, ProjectApplication


APP_CHOICES = (("U", "Join an existing project"),)

if settings.ALLOW_NEW_PROJECTS:
    APP_CHOICES = APP_CHOICES + (("P", "Apply to start a new project"),)


class StartApplicationForm(forms.Form):
    application_type = forms.ChoiceField(choices=APP_CHOICES, widget=forms.RadioSelect())


class ApplicantForm(forms.ModelForm):
    username = forms.RegexField(
        "^%s$" % settings.USERNAME_VALIDATION_RE,
        label=six.u("Requested username"),
        max_length=settings.USERNAME_MAX_LENGTH,
        help_text=(
            settings.USERNAME_VALIDATION_ERROR_MSG + " and has a max length of %s." % settings.USERNAME_MAX_LENGTH
        ),
    )
    telephone = forms.CharField(
        required=True,
        label=six.u("Office Telephone"),
        help_text=six.u("Used for emergency contact and password reset service."),
        validators=[validate_phone_number],
    )
    mobile = forms.CharField(
        required=False,
        validators=[validate_phone_number],
    )
    fax = forms.CharField(
        required=False,
        validators=[validate_phone_number],
    )

    class Meta:
        model = Applicant
        fields = [
            "email",
            "username",
            "title",
            "short_name",
            "full_name",
            "institute",
            "department",
            "position",
            "telephone",
            "mobile",
            "supervisor",
            "address",
            "city",
            "postcode",
            "country",
            "fax",
        ]

    def clean(self):
        data = super(ApplicantForm, self).clean()

        for key in [
            "short_name",
            "full_name",
            "email",
            "position",
            "supervisor",
            "department",
            "telephone",
            "mobile",
            "fax",
            "address",
            "city",
            "postcode",
        ]:
            if key in data and data[key]:
                data[key] = data[key].strip()

        return data

    def __init__(self, *args, **kwargs):
        super(ApplicantForm, self).__init__(*args, **kwargs)
        self.fields["title"].required = True
        self.fields["short_name"].required = True
        self.fields["short_name"].help_text = "This is typically your given name. For example enter 'Fred' here."
        self.fields["full_name"].required = True
        self.fields["full_name"].help_text = "This is typically your full name. For example enter 'Fred Smith' here."
        self.fields["username"].label = "Requested username"
        self.fields["username"].required = True
        self.fields["institute"].required = True
        self.fields["institute"].help_text = (
            "If your institute is not listed please contact %s" % settings.ACCOUNTS_EMAIL
        )
        self.fields["department"].required = True

    def clean_username(self):
        username = self.cleaned_data["username"]
        if username:
            try:
                validate_username_for_new_person(username)
            except UsernameException as e:
                raise forms.ValidationError(e.args[0])

            return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        users = Person.objects.filter(email__exact=email)
        if users.count() > 0:
            raise forms.ValidationError(
                six.u("An account with this email already exists. Please email %s") % settings.ACCOUNTS_EMAIL
            )
        clean_email(email)
        return email


class UserApplicantForm(ApplicantForm):
    institute = forms.ModelChoiceField(queryset=None, required=True)

    def __init__(self, *args, **kwargs):
        super(UserApplicantForm, self).__init__(*args, **kwargs)
        self.fields["institute"].queryset = Institute.active.filter(Q(saml_entityid="") | Q(saml_entityid__isnull=True))

    def save(self, commit=True):
        applicant = super(UserApplicantForm, self).save(commit=commit)
        if commit:
            applicant.save()
        return applicant

    class Meta:
        model = Applicant
        exclude = ["email"]


class AafApplicantForm(UserApplicantForm):
    def __init__(self, *args, **kwargs):
        super(AafApplicantForm, self).__init__(*args, **kwargs)
        del self.fields["institute"]

    class Meta:
        model = Applicant
        exclude = ["email", "institute"]


class CommonApplicationForm(forms.ModelForm):
    aup = forms.BooleanField(error_messages={"required": "You must accept to proceed."})
    application_type = forms.ChoiceField(choices=APP_CHOICES, widget=forms.RadioSelect())

    def __init__(self, *args, **kwargs):
        super(CommonApplicationForm, self).__init__(*args, **kwargs)
        aup_url = getattr(settings, "AUP_URL", None)
        if aup_url is None:
            aup_url = reverse("kg_aup")
        self.fields["aup"].label = mark_safe(
            six.u("I have read and agree to the " '<a href="%s" target="_blank">Acceptable Use Policy</a>') % aup_url
        )

    class Meta:
        model = ProjectApplication
        fields = ["needs_account"]


class NewProjectApplicationForm(forms.ModelForm):
    name = forms.CharField(label="Project Title", widget=forms.TextInput(attrs={"size": 60}))
    description = forms.CharField(
        max_length=1000, widget=forms.Textarea(attrs={"class": "vLargeTextField", "rows": 10, "cols": 40})
    )
    additional_req = forms.CharField(
        label="Additional requirements",
        widget=forms.Textarea(attrs={"class": "vLargeTextField", "rows": 10, "cols": 40}),
        help_text=six.u("Do you have any special requirements?"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(NewProjectApplicationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = ProjectApplication
        fields = [
            "name",
            "description",
            "additional_req",
        ]


class ExistingProjectApplicationForm(forms.ModelForm):
    project = forms.ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        super(ExistingProjectApplicationForm, self).__init__(*args, **kwargs)
        self.fields["project"].queryset = Project.active.all()

    class Meta:
        model = ProjectApplication
        fields = ["project"]


class InviteUserApplicationForm(forms.ModelForm):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        self.cleaned_data = None
        self.fields = None
        super(InviteUserApplicationForm, self).__init__(*args, **kwargs)
        self.fields["email"].required = True
        self.fields["header_message"].required = True

    class Meta:
        model = ProjectApplication
        fields = ["email", "make_leader", "header_message"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        clean_email(email)
        return email


class UnauthenticatedInviteUserApplicationForm(forms.Form):
    email = forms.EmailField()
    captcha = CaptchaField(
        label=six.u("CAPTCHA"), help_text=six.u("Please enter the text displayed in the image above.")
    )

    def clean_email(self):
        email = self.cleaned_data["email"]

        query = Person.active.filter(email=email)
        if query.count() > 0:
            raise forms.ValidationError(
                six.u("E-Mail address is already in use. If you already have an account, please login.")
            )

        clean_email(email)
        return email


def approve_project_form_generator(application, auth):
    if application.project is None:
        # new project
        include_fields = ["additional_req", "needs_account"]
    else:
        # existing project
        include_fields = ["make_leader", "needs_account"]

    class ApproveProjectForm(forms.ModelForm):
        if application.project is None:
            # new project
            additional_req = forms.CharField(
                label="Additional requirements",
                widget=forms.Textarea(attrs={"class": "vLargeTextField", "rows": 10, "cols": 40}),
                help_text=six.u("Do you have any special requirements?"),
                required=False,
            )

        class Meta:
            model = ProjectApplication
            fields = include_fields

        def __init__(self, *args, **kwargs):
            super(ApproveProjectForm, self).__init__(*args, **kwargs)
            self.fields["needs_account"].label = six.u("Does this person require a cluster account?")
            self.fields["needs_account"].help_text = six.u("Will this person be working on the project?")

    return ApproveProjectForm


def admin_approve_project_form_generator(application, auth):
    parent = approve_project_form_generator(application, auth)
    if application.project is None:
        # new project
        include_fields = ["pid", "additional_req", "needs_account"]
    else:
        # existing project
        include_fields = ["make_leader", "needs_account"]

    class AdminApproveProjectForm(parent):
        if application.project is None:
            # new project
            additional_req = forms.CharField(
                label="Additional requirements",
                widget=forms.Textarea(attrs={"class": "vLargeTextField", "rows": 10, "cols": 40}),
                help_text=six.u("Do you have any special requirements?"),
                required=False,
            )
            pid = forms.RegexField(
                "^%s$" % settings.PROJECT_VALIDATION_RE,
                required=False,
                label="PID",
                help_text="Leave blank for auto generation",
                error_messages={"invalid": settings.PROJECT_VALIDATION_ERROR_MSG},
            )

        class Meta:
            model = ProjectApplication
            fields = include_fields

        def clean_pid(self):
            pid = self.cleaned_data["pid"]
            if not pid:
                return pid
            try:
                Institute.objects.get(name=pid)
                raise forms.ValidationError(six.u("Project ID already in system"))
            except Institute.DoesNotExist:
                pass
            try:
                Project.objects.get(pid=pid)
                raise forms.ValidationError(six.u("Project ID already in system"))
            except Project.DoesNotExist:
                pass
            return pid

    return AdminApproveProjectForm


class PersonSetPassword(forms.Form):
    """
    A form that lets a user change set his/her password without entering the
    old password
    """

    new_password1 = forms.CharField(label=six.u("New password"), widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=six.u("New password confirmation"), widget=forms.PasswordInput)

    def __init__(self, person, *args, **kwargs):
        self.person = person
        super(PersonSetPassword, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        return validate_password(self.person.username, password1, password2)

    def save(self, commit=True):
        self.person.set_password(self.cleaned_data["new_password1"])
        if commit:
            self.person.save()
        return self.person


class PersonVerifyPassword(forms.Form):
    """
    A form that lets a user verify his old password and updates it on all
    datastores.
    """

    password = forms.CharField(label="Existing password", widget=forms.PasswordInput)

    def __init__(self, person, *args, **kwargs):
        self.person = person
        super(PersonVerifyPassword, self).__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data["password"]
        person = Person.objects.authenticate(username=self.person.username, password=password)

        if person is None:
            raise forms.ValidationError(six.u("Password is incorrect."))

        assert person == self.person

        if not person.is_active or person.is_locked():
            raise forms.ValidationError(six.u("Person is locked."))

        return password

    def save(self, commit=True):
        password = self.cleaned_data["password"]
        self.person.set_password(password)
        if commit:
            self.person.save()
        return self.person


class ApplicantReplace(forms.Form):
    replace_applicant = ajax_select.fields.AutoCompleteSelectField(
        "person", required=True, help_text="Do not set unless absolutely positive sure."
    )

    def __init__(self, application, *args, **kwargs):
        self.application = application
        super(ApplicantReplace, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        replace_applicant = self.cleaned_data["replace_applicant"]
        if replace_applicant is not None:
            self.application.new_applicant = None
            self.application.existing_person = replace_applicant
            self.application.save()
