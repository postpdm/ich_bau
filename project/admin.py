from django.contrib import admin

from .models import Project, Task, Milestone, TaskLink

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

admin.site.register(
    Task,
    )

admin.site.register(
    Milestone,
    )

admin.site.register(
    TaskLink,
    list_display=[
        "maintask", 
        "subtask",
    ], )
