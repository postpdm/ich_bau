from django.db import models

from commons.models import BaseStampedModel
from django.contrib.auth.models import User

from django.db import transaction
import reversion

from ich_bau.profiles.notification_helper import Send_Notification
from ich_bau.profiles.models import Profile
from ich_bau.profiles.messages import *

import markdown

class Contract(BaseStampedModel):
    shortname = models.CharField(max_length=255)
    fullname = models.CharField(max_length=255, verbose_name = 'Full name!')
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['fullname']

    def __str__(self):
        return self.fullname

    def get_absolute_url(self):
        return "/crm/contract/%i/" % self.id

    def description_html(self):
        return markdown.markdown(self.description)

