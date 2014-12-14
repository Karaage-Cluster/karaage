from django import forms

from allocations.models import AllocationPeriod


class AllocationPeriodForm(forms.ModelForm):

    class Meta:
        models = AllocationPeriod
        fields = [
            name,
            start,
            end,
        ]
