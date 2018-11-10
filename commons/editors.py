from django import forms
from pagedown.widgets import PagedownWidget

from bootstrap3_datetime.widgets import DateTimePicker

def MarkDownEditor_Field(arg_required=False):
    return forms.CharField(required=arg_required, widget=PagedownWidget())

def DateTime_Field(arg_required=False):
    return forms.DateField( required = False, widget=DateTimePicker(options={"format": "YYYY-MM-DD", "pickTime": False}))
