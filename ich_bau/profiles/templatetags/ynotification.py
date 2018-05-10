from django import template

register = template.Library()

from ich_bau.profiles.models import Notification, GetUserNoticationsQ

from django.utils.html import format_html

# подсчитать кол-во уведомлений пользователю
@register.simple_tag(name='unread_notification_count', takes_context=True)
def unread_notification_count(context):
    m_count = 0

    request = context['request']
    u = request.user
    if ( u is None ) or not ( u.is_authenticated ):
        return ''

    m_count = GetUserNoticationsQ(u, True).count()
    if m_count == 0:
        html_str = '<i class="fa fa-envelope-o"></i>'
    else:
        html_str = '<i class="fa fa-envelope"></i> <span class="badge"> %i </span>' % m_count

    return format_html(html_str)

@register.simple_tag(name='main_message', takes_context=False)
def main_message():
    from django.conf import settings

    mm = settings.MAIN_MESSAGE
    if mm:
        return format_html('<div class="alert alert-info" role="alert">' + mm + '</div>')
    else:
        return None