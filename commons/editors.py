from django import forms
from pagedown.widgets import PagedownWidget

def MarkDownEditor_Field(arg_required=False):
    return forms.CharField(required=arg_required, widget=PagedownWidget())