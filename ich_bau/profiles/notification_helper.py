from .models import Notification
from .messages import decode_json2msg
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.models import Site

def Send_Notification( ArgFromUser, Arg2User, Arg_MsgTxt, Arg_Url ):
    n = Notification()
    n.sender_user = ArgFromUser
    n.reciever_user = Arg2User
    n.msg_txt = Arg_MsgTxt
    n.msg_url = Arg_Url
    n.save()

    # if users have a mail's
    if settings.EMAIL_HOST_USER and n.reciever_user.email:
        html_message = '<p><a href="' + Site.objects.get_current().domain + n.get_absolute_url() + '">' + decode_json2msg( Arg_MsgTxt ) + '</a></p>'
        send_mail( decode_json2msg( Arg_MsgTxt ),
                   html_message,
                   settings.EMAIL_HOST_USER,
                   [n.reciever_user.email],
                   fail_silently=False,
                 )
