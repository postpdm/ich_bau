import re

from django import forms

from .models import Profile, Profile_Affiliation, PROFILE_TYPE_CHOICES_EDITOR

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
    profile_type = forms.ChoiceField(required=True, choices=PROFILE_TYPE_CHOICES_EDITOR)
    class Meta:
        model = Profile
        fields = [ "profile_type", ] + form_fields

class Profile_AffiliationForm(forms.ModelForm):
    class Meta:
        model = Profile_Affiliation
        fields = [ 'sub_profile' , ]

    def __init__(self, *args, **kwargs):
        super(Profile_AffiliationForm, self).__init__(*args, **kwargs)
        # форма работает в режиме создания (смотрим 'initial')
        mp = kwargs.pop('initial', None)['main_profile']

        # отображать только не привязанные
        if mp:
            self.fields['sub_profile'].queryset = mp.list_of_avail_for_affiliate()
