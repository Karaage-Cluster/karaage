from django import forms

from karaage.allocations.models import AllocationPeriod


class AllocationPeriodForm(forms.ModelForm):

    class Meta:
        model = AllocationPeriod
        fields = [
            'name',
            'start',
            'end',
        ]
