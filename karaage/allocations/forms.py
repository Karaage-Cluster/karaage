from datetime import datetime

from django import forms

from karaage.allocations.models import (
    Allocation,
    AllocationPeriod,
    AllocationPool,
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
