from .models import Notification
from django.core.mail import send_mail

def Send_Notification( ArgFromUser, Arg2User, Arg_MsgTxt, Arg_Url ):
    n = Notification()
    n.sender_user = ArgFromUser
    n.reciever_user = Arg2User
    n.msg_txt = Arg_MsgTxt
    n.msg_url = Arg_Url
    n.save()

    # if users have a mail's
    if n.sender_user.email and n.reciever_user.email:
        send_mail( 'Arg_MsgTxt',
                   Arg_Url,
                   n.sender_user.email,
                   [n.reciever_user.email],
                   fail_silently=False,
                 )
