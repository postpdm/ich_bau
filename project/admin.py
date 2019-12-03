from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import Project, Member, TaskKind, TaskDomain, Task, Task2Domain, Milestone, TaskLink

admin.site.register(
    Project,
    list_display=[
        "fullname",
        "active_flag",
        "private_type",
        "created_at",
        "created_user",
        "modified_at",
        "modified_user",
    ],)

admin.site.register(
    Member,
    list_display=[
        "member_profile",
        "project",
        "admin_flag",
        ]
    )

admin.site.register(
    TaskKind,
    list_display=[
        "name",
        ]
    )

admin.site.register(TaskDomain, MPTTModelAdmin)

admin.site.register(
    Task,
    list_display=[
        "fullname",
        "project",
        "kind",
        "created_at",
        "created_user",
        "modified_at",
        "modified_user",
        "finished_fact_at",
        "important",
        ]
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

admin.site.register(
    Task2Domain,
    list_display=[
        "taskdomain",
        "task",
    ], )
