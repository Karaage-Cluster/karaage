# Copyright 2011 VPAC
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

from karaage.people.models import Institute
from karaage.projects.models import Project


class InstituteForm(forms.ModelForm):

    def clean_saml_entityid(self):
        if self.cleaned_data['saml_entityid'] == "":
            return None
        return self.cleaned_data['saml_entityid']

    class Meta:
        model = Institute
        exclude = ('delegates',)

    def clean_name(self):
        name = self.cleaned_data['name']
        try:
            project = Project.objects.get(pid=name)
            raise forms.ValidationError(u'Institute name already in system')
        except Project.DoesNotExist:
            return name
