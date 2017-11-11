# contract forms

from django import forms
from crm.models import Contract

from django.forms.widgets import HiddenInput

from bootstrap3_datetime.widgets import DateTimePicker

class ContractForm(forms.ModelForm):
    start_date = forms.DateField( required = False, widget=DateTimePicker(options={"format": "YYYY-MM-DD", "pickTime": False}))
    end_date   = forms.DateField( required = False, widget=DateTimePicker(options={"format": "YYYY-MM-DD", "pickTime": False}))

    class Meta:
        model = Contract
        fields = ['shortname','fullname', 'description','start_date', 'end_date' ]

from ich_bau.profiles.models import Profile