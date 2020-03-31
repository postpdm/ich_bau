from django import template

register = template.Library()

@register.simple_tag(name='site_version_info')
def site_version_info():
    return 'v0.0023 at 01.04.2020'
