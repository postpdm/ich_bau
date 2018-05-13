from django import forms
from pagedown.widgets import PagedownWidget

def MarkDownEditor_Field():
    return forms.CharField(widget=PagedownWidget())