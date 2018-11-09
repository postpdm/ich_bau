import os
import uuid

from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from .messages import decode_json2msg
from django_cryptography.fields import encrypt
from project.repo_wrapper import Gen_Repo_User_PW

class Notification(models.Model):
    sender_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name = 'sender_user' )
    created_at = models.DateTimeField(default=timezone.now)
    reciever_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name = 'reciever_user')
    readed_at = models.DateTimeField( blank=True, null = True )
    msg_txt = models.CharField(max_length=255, blank=False)
    msg_url = models.URLField(max_length=75, blank=True, null = True)

    def decode_msg( self ):
        return decode_json2msg( self.msg_txt )

    def get_unreaded( self ):
        return self.readed_at is None

    def mark_readed(self):
        if self.readed_at is None:
            self.readed_at = timezone.now()
            self.save()
        # иначе - ничего не делать

    def get_absolute_url(self):
        return "/notification/%i/" % self.id

def GetUserNoticationsQ( arg_user, arg_new ):
    return Notification.objects.filter(reciever_user = arg_user, readed_at__isnull=arg_new).order_by('-created_at')

def avatar_upload(instance, filename):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join("avatars", filename)

import markdown

PROFILE_TYPE_BOT = 0
PROFILE_TYPE_USER = 1
PROFILE_TYPE_PEOPLE = 2 # without accunt
PROFILE_TYPE_DEPARTAMENT = 3
PROFILE_TYPE_ORG = 4
PROFILE_TYPE_RESOURCE = 5

PROFILE_TYPE_LIST = ( PROFILE_TYPE_BOT, PROFILE_TYPE_USER, PROFILE_TYPE_PEOPLE, PROFILE_TYPE_DEPARTAMENT, PROFILE_TYPE_ORG, PROFILE_TYPE_RESOURCE )

PROFILE_TYPE_CHOICES_EDITOR = (
  ( PROFILE_TYPE_PEOPLE, 'People' ),
  ( PROFILE_TYPE_DEPARTAMENT, 'Departament' ),
  ( PROFILE_TYPE_ORG, 'Organization' ),
  ( PROFILE_TYPE_RESOURCE, 'Resource' ),
)

PROFILE_TYPE_CHOICES = (
  ( PROFILE_TYPE_BOT, 'Bot' ),
  ( PROFILE_TYPE_USER, 'User' ),
) + PROFILE_TYPE_CHOICES_EDITOR

class Profile(models.Model):
    profile_type = models.PositiveSmallIntegerField( blank=False, null=False, default = PROFILE_TYPE_USER )
    user = models.OneToOneField(User, on_delete=models.PROTECT, blank=True, null=True, related_name="profile")
    name = models.CharField(max_length=75, blank=True)
    avatar = models.ImageField(upload_to=avatar_upload, blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.CharField(max_length=250, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)

    repo_pw = encrypt( models.CharField(max_length=100, blank=True) )

    def save(self, *args, **kwargs):
        if self.profile_type in PROFILE_TYPE_LIST: # check for profile type
            self.modified_at = timezone.now()
            if ( self.profile_type in ( PROFILE_TYPE_USER, PROFILE_TYPE_BOT ) ) and ( ( self.repo_pw is None ) or ( self.repo_pw == '' ) ):
                self.repo_pw = Gen_Repo_User_PW()

            return super(Profile, self).save(*args, **kwargs)
        else:
            raise Exception("Cannot save - wrong profile type!")

    def __str__(self):
        return self.display_name

    def get_absolute_url(self):
        return reverse_lazy('profiles_detail', kwargs={ 'pk': self.id} )

    @property
    def is_user(self):
        print( self.profile_type, PROFILE_TYPE_USER )
        return self.profile_type == PROFILE_TYPE_USER

    @property
    def display_name(self):
        s = ''
        if self.name:
            s = self.name
        else:
            if self.user:
                s = self.user.username
        return s + " (" + PROFILE_TYPE_CHOICES[self.profile_type][1] + ")"

    def sub_profiles(self):
        return Profile_Affiliation.objects.filter(main_profile=self )

    def main_profiles(self):
        return Profile_Affiliation.objects.filter(sub_profile=self )

    def list_of_avail_for_affiliate(self):
        return Profile.objects.all().exclude( id = self.id ).exclude( sub_profile__main_profile_id = self.id )

    def description_html(self):
        return markdown.markdown(self.description)

# датасет профилей, принадлежащих юзерам
def Get_Users_Profiles():
    return Profile.objects.filter( profile_type = PROFILE_TYPE_USER )

class Profile_Affiliation(models.Model):
    main_profile = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name = 'main_profile' )
    sub_profile = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name = 'sub_profile' )

    class Meta:
        unique_together = ( "main_profile", "sub_profile")

    def save(self, *args, **kwargs):
        if ( self.main_profile == self.sub_profile ):
            raise Exception("Cannot save - profile cannot affiliate to itself!")
        else:
            return super(Profile_Affiliation, self).save(*args, **kwargs)

class Profile_Control_User(models.Model):
    controlled_profile = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name = 'controlled_profile' )
    control_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="control_user")

    class Meta:
        unique_together = ( "controlled_profile", "control_user" )