from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class BaseStampedModel(models.Model):
    created_at = models.DateTimeField( blank=False, null=False )
    created_user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True, related_name = "%(class)s_created_user" )
    # после создания объекта modified_at равен created_at
    modified_at = models.DateTimeField( blank=False, null=False )
    # после создания объекта modified_user равен created_user
    modified_user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True, related_name = "%(class)s_modified_user" )

    # этот класс - базовый и абстрактный, в db его включать не надо
    class Meta:
        abstract = True

    def set_change_user(self, argUser):
        # указать автора изменений. Если нет создателя - внести. Модификатора обновить в любом случае
        if self.created_user is None:
            self.created_user = argUser
        self.modified_user = argUser

    def save(self, *args, **kwargs):
        n = timezone.now()
        # указать дату создания
        if not self.created_at:
            self.created_at = n
        # указать дату изменения
        self.modified_at = n
        if ( self.created_user is None ) or ( self.modified_user is None ):
            raise Exception("Cannot save - user is missing.")
        else:
            return super(BaseStampedModel, self).save(*args, **kwargs)