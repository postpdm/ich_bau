import os
import uuid

from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User

class Notification(models.Model):
    sender_user = models.ForeignKey(User, related_name = 'sender_user' )
    created_at = models.DateTimeField(default=timezone.now)
    reciever_user = models.ForeignKey(User, related_name = 'reciever_user')
    readed_at = models.DateTimeField( blank=True, null = True )
    msg_txt = models.CharField(max_length=255, blank=False)
    msg_url = models.URLField(max_length=75, blank=True, null = True)
    
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

class Profile(models.Model):

    user = models.OneToOneField(User, related_name="profile")
    name = models.CharField(max_length=75, blank=True)
    avatar = models.ImageField(upload_to=avatar_upload, blank=True)
    bio = models.TextField(blank=True)
    affiliation = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.CharField(max_length=250, blank=True)
    twitter_username = models.CharField("Twitter Username", max_length=100, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.modified_at = timezone.now()
        return super(Profile, self).save(*args, **kwargs)

    @property
    def display_name(self):
        if self.name:
            return self.name
        else:
            return self.user.username
            
    def bio_html(self):
        return markdown.markdown(self.bio)            