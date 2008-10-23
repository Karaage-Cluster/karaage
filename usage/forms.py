from django import forms
from django.forms.extras.widgets import SelectDateWidget
import datetime

todays_year = datetime.date.today().year


class UsageSearchForm(forms.Form):
    terms = forms.CharField(help_text="Searchs against Project IDs, Project names and Institute names (optional)", required=False)
    start_date = forms.DateField(widget=SelectDateWidget(years=range(todays_year, 2002, -1)))
    end_date = forms.DateField(initial=datetime.date.today().strftime('%Y-%m-%d'), widget=SelectDateWidget(years=range(todays_year, 2002, -1)))

