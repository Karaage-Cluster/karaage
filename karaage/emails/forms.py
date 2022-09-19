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

from ajax_select.fields import AutoCompleteSelectField
from django import forms

from karaage.people.models import Person


EMAIL_GROUPS = (
    ("leaders", "All Project Leaders (active projects only)"),
    ("users", "All Active Users"),
    ("cluster_users", "All Users with cluster accounts"),
)


class EmailForm(forms.Form):
    subject = forms.CharField(widget=forms.TextInput(attrs={"size": 60}))
    body = forms.CharField(widget=forms.Textarea(attrs={"class": "vLargeTextField", "rows": 10, "cols": 40}))

    def get_data(self):
        return self.cleaned_data["subject"], self.cleaned_data["body"]


class BulkEmailForm(EmailForm):
    group = forms.ChoiceField(choices=EMAIL_GROUPS)
    institute = AutoCompleteSelectField("institute", required=False, label="Institute")
    project = AutoCompleteSelectField("project", required=False, label="Project")

    def get_person_query(self):
        person_query = Person.active.all()

        group = self.cleaned_data["group"]
        if group == "leaders":
            person_query = person_query.filter(leads__isnull=False)

        elif group == "users":
            pass

        elif group == "cluster_users":
            person_query = person_query.filter(account__isnull=False)

        else:
            person_query = None

        institute = self.cleaned_data["institute"]
        if institute is not None:
            person_query = person_query.filter(institute=institute)

        project = self.cleaned_data["project"]
        if project is not None:
            person_query = person_query.filter(groups__project=project)

        return person_query
