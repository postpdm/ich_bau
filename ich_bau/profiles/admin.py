from django.contrib import admin

from .models import Profile, Profile_Affiliation


admin.site.register(
    Profile,
    list_display=[
        "user",
        "name",
        "avatar",
        "location",
        "website",
        "twitter_username",
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
        "twitter_username",
    ]
)

admin.site.register(
    Profile_Affiliation,
    list_display=[
        "main_profile",
        "sub_profile",
    ],
)