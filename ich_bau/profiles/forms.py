import re

from django import forms

from .models import Profile, PROFILE_TYPE_CHOICES

form_fields = [
            "name",
            "avatar",
            "description",
            "location",
            "website",
        ]

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = form_fields

class ContactProfileForm(ProfileForm):
    profile_type = forms.ChoiceField(required=True, choices=PROFILE_TYPE_CHOICES)
    class Meta:
        model = Profile
        fields = [ "profile_type", ] + form_fields
