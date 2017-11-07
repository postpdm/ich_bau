from django import template

register = template.Library()

#from django.utils.html import format_html

@register.simple_tag(name='site_version_info')
def site_version_info():
    return 'v0.0 at 20.10.2017'
    #return #format_html('<i class="fa ' + PROFILE_TYPE_ICONS[ arg ][1] + ' fa-4x"></i>')