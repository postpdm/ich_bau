from django import forms

from bootstrap3_datetime.widgets import DateTimePicker

from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget

def TextEditor_Field(arg_required=False):
    return forms.CharField(widget=SummernoteWidget())

def DateTime_Field(arg_required=False):
    return forms.DateField( required = False, widget=DateTimePicker(options={"format": "YYYY-MM-DD", "pickTime": False}))
