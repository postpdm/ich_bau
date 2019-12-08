from django.contrib import admin

from .models import Profile, Profile_Affiliation, Profile_Manage_User

admin.site.register(
    Profile,
    list_display=[
        "profile_type",
        "user",
        "name",
        "avatar",
        "location",
        "website",
        "created_at",
    ],
    list_filter=[
        "created_at",
    ],
    search_fields=[
        "user__username",
        "user__email",
        "name",
        "location",
        "website",
    ]
)

admin.site.register(
    Profile_Affiliation,
    list_display=[
        "main_profile",
        "sub_profile",
    ],
)

admin.site.register(
    Profile_Manage_User,
    list_display=[
        "manager_user",
        "managed_profile", 
    ],
    
)