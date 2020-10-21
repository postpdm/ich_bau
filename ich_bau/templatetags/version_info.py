from django import template

register = template.Library()

@register.simple_tag(name='site_version_info')
def site_version_info():
    return 'v0.0037 at 21.10.2020'
