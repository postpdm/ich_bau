from django.contrib import admin

from .models import Project

admin.site.register(
    Project,
    list_display=[
        "fullname",
        "active_flag",
        "private_flag",
        "created_at",
        "created_user",
        "modified_at",
        "modified_user",
    ],)