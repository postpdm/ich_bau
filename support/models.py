from django.db import models as django_models

from project.models import Project

# Create your models here.

class SupportProject(django_models.Model):
    project = django_models.OneToOneField(Project, on_delete=django_models.PROTECT, related_name = "for_support_purposes", unique=True )



