# Copyright 2014 The University of Melbourne
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

from datetime import datetime

from django import forms

from karaage.allocations.models import (
    Allocation,
    AllocationPeriod,
    Grant,
)
from karaage.machines.models import ResourcePool
from karaage.schemes.models import Scheme


class AllocationPeriodForm(forms.ModelForm):

    class Meta:
        model = AllocationPeriod
        fields = [
            'name',
            'start',
            'end',
        ]


class AllocationForm(forms.ModelForm):

    period = forms.ModelChoiceField(
        AllocationPeriod.objects.filter(end__gt=datetime.now())
    )
    resource_pool = forms.ModelChoiceField(
        ResourcePool.objects.all()
    )

    def __init__(self, project, *args, **kwargs):
        super(AllocationForm, self).__init__(*args, **kwargs)
        self.fields['grant'].queryset = Grant.objects.filter(project=project)

    class Meta:
        model = Allocation
        fields = [
            'description',
            'grant',
            'quantity',
        ]


class GrantForm(forms.ModelForm):

    class Meta:
        model = Grant
        fields = [
            'scheme',
            'date',
            'description',
            'begins',
            'expires',
        ]


class SchemeForm(forms.ModelForm):

    class Meta:
        model = Scheme
        fields = [
            'name',
            'description',
            'opened',
            'closed',
        ]
