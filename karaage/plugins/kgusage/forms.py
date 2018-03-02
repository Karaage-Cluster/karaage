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

import datetime

from django import forms
from django.forms.widgets import SelectDateWidget


todays_year = datetime.date.today().year


class UsageSearchForm(forms.Form):
    terms = forms.CharField(
        help_text="Searchs against Project IDs, Project names and "
        "Institute names (optional)",
        required=False)
    start_date = forms.DateField(
        widget=SelectDateWidget(years=range(todays_year, 2002, -1)))
    end_date = forms.DateField(
        initial=datetime.date.today().strftime('%Y-%m-%d'),
        widget=SelectDateWidget(years=range(todays_year, 2002, -1)))
