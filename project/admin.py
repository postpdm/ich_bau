from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import Project, Member, TaskKind, TaskDomain, Task, Task2Domain, Milestone, TaskLink, ScheduleItem, ScheduleItem_Task, Task_Property_Type

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

admin.site.register(
    ScheduleItem,
    list_display=[
        "schedule_date_start",
        "schedule_date_end",
        "schedule_profile",
    ],
    )

admin.site.register(
    ScheduleItem_Task,
    list_display=[
        "schedule_item",
        "scheduledtask",
    ],
    )

admin.site.register(
    Task_Property_Type,
    )
