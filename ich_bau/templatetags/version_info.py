from django import template

register = template.Library()

@register.simple_tag(name='site_version_info')
def site_version_info():
    return 'v0.0041 at 21.04.2021'
