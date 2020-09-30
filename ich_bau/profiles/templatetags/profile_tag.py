from django import template

register = template.Library()

from django.utils.html import format_html

from ich_bau.profiles.models import *

PROFILE_TYPE_ICONS = (
  ( PROFILE_TYPE_BOT, 'fa-meh-o' ),
  ( PROFILE_TYPE_USER, 'fa-user' ),
  ( PROFILE_TYPE_PEOPLE, 'fa-bars' ),
  ( PROFILE_TYPE_DEPARTAMENT, 'fa-users' ),
  ( PROFILE_TYPE_ORG, 'fa-university' ),
  ( PROFILE_TYPE_RESOURCE, 'fa-cogs' ),
  ( PROFILE_TYPE_FOLDER, 'fa-folder' ),
)

@register.simple_tag(name='fa_profile_icon', takes_context=True)
def fa_profile_icon(context, arg):
    try:
        return format_html('<i class="fa ' + PROFILE_TYPE_ICONS[ arg ][1] + ' fa-4x"></i>')
    except:
        return None

@register.simple_tag(name='profile_type_name', takes_context=True)
def profile_type_name(context, arg):
    try:
        return PROFILE_TYPE_CHOICES[arg][1]
    except:
        return None
