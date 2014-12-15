from django import forms

from karaage.allocations.models import (
    Allocation,
    AllocationPeriod,
    Grant,
)
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

    class Meta:
        model = Allocation
        fields = [
            'description',
            'grant',
            'quantity',
            'allocation_pool',
        ]


class GrantForm(forms.ModelForm):

    class Meta:
        model = Grant
        fields = [
            'project',
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
