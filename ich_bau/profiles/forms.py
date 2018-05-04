import re

from django import forms

from .models import Profile

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = [
            "name",
            "avatar",
            "description",
            "location",
            "website",
        ]

class ContactProfileForm(ProfileForm):
    class Meta:
        model = Profile        
        fields = [
            "profile_type",
            "name",
            "avatar",
            "description",
            "location",
            "website",
        ]        #fields + 
