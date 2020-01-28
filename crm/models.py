from django.db import models

from commons.models import BaseStampedModel
from django.contrib.auth.models import User

from django.db import transaction
import reversion

@reversion.register()
class Contract(BaseStampedModel):
    shortname = models.CharField(max_length=255, blank=True, null=True)
    fullname = models.CharField(max_length=255, verbose_name = 'Full name!')
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField( blank=True, null=True )
    end_date = models.DateField( blank=True, null=True )

    class Meta:
        ordering = ['fullname']

    def __str__(self):
        if self.shortname:
            s = self.shortname + ' ' + self.fullname
        else:
            s = self.fullname
        return s

    def get_absolute_url(self):
        return "/crm/contract/%i/" % self.id

    def description_html(self):
        return self.description
