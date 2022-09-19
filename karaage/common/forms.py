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

""" Forms for Karaage use. """

import re

import six
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from karaage.common.models import COMMENT, LogEntry

from .passwords import assert_strong_password


def validate_phone_number(value):
    if re.match(r"^[0-9a-zA-Z\.( )+-]+$", value) is None:
        raise ValidationError(f"{value} contains invalid characters")
    if re.search(r"[0-9]", value) is None:
        raise ValidationError(f"{value} should contain at least one digit")


def validate_password(username, password1, password2=None, old_password=None):
    # password1 is mandatory, it must be given in order to proceed.
    if password1 is None:
        raise forms.ValidationError(six.u("The first password was not given."))

    # password2 is an optional parameter, and may be None
    if password2 is not None and password1 != password2:
        raise forms.ValidationError(six.u("The two password fields didn't match."))

    # Now we can check password1
    try:
        assert_strong_password(username, password1, old_password)
    except ValueError as e:
        raise forms.ValidationError(six.u("Your password was found to be insecure: %s." % str(e)))

    # If password1 is ok, return it.
    return password1


def clean_email(email):
    email_match_type = "exclude"
    email_match_list = []
    if hasattr(settings, "EMAIL_MATCH_TYPE"):
        email_match_type = settings.EMAIL_MATCH_TYPE
    if hasattr(settings, "EMAIL_MATCH_LIST"):
        email_match_list = settings.EMAIL_MATCH_LIST

    found = False
    for string in email_match_list:
        m = re.search(string, email, re.IGNORECASE)
        if m is not None:
            found = True
            break

    message = "This email address cannot be used."
    if hasattr(settings, "EMAIL_MATCH_MSG"):
        message = settings.EMAIL_MATCH_MSG
    if email_match_type == "include":
        if not found:
            raise forms.ValidationError(message)
    elif email_match_type == "exclude":
        if found:
            raise forms.ValidationError(message)
    else:
        raise forms.ValidationError("Oops. Nothing is valid. Sorry.")


class CommentForm(forms.ModelForm):
    """Comment form."""

    class Meta:
        model = LogEntry
        fields = ["change_message"]

    def __init__(self, obj, request, instance=None, **kwargs):
        self.obj = obj
        self.request = request
        if instance is not None:
            assert instance.action_flag == COMMENT
            assert obj == instance.content_object
        super(CommentForm, self).__init__(instance=instance, **kwargs)

    def save(self, commit=True):
        log = super(CommentForm, self).save(commit=False)
        log.content_object = self.obj
        log.object_repr = six.text_type(self.obj)
        log.action_flag = COMMENT
        log.user = self.request.user

        if commit:
            log.save()

        return log


class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=30)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
