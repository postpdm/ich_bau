# contract forms

from django import forms
from crm.models import Contract

from django.forms.widgets import HiddenInput

from commons.editors import DateTime_Field, TextEditor_Field

class ContractForm(forms.ModelForm):
    description = TextEditor_Field()
    start_date = DateTime_Field()
    end_date   = DateTime_Field()

    class Meta:
        model = Contract
        fields = ['shortname','fullname', 'description','start_date', 'end_date' ]

from ich_bau.profiles.models import Profile