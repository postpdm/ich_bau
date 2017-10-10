from django import template

register = template.Library()

from django.utils.html import format_html

@register.simple_tag(name='percent', takes_context=False)
def percent(arg1, arg2):
    if ( arg1 == 0 ) or ( arg2 == 0 ):
        return 0
    else:    
        return int( 100*arg1/arg2 )