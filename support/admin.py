from django.contrib import admin

# Register your models here.

from .models import SupportProject

admin.site.register(
    SupportProject,

    )