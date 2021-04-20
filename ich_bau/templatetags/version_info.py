from django import template

register = template.Library()

@register.simple_tag(name='site_version_info')
def site_version_info():
    return 'v0.0040 at 20.04.2021'
