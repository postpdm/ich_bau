from .models import Notification
from .messages import decode_json2msg, MSG_NOTFY_TYPES
from commons.utils import get_full_site_url

from django.core.mail import send_mail
from django.conf import settings

from django.template.loader import render_to_string

def Send_Notification( ArgFromUser, Arg2User, Arg_ContentType, Arg_ObjectID, Arg_MSG_TYPE, Arg_MsgTxt, Arg_Url, Arg_Additional_Msg_Tags = None ):
    if not Arg_MSG_TYPE in MSG_NOTFY_TYPES:
        raise Exception ("Wrong type for Arg_MSG_TYPE")

    n = Notification()
    n.sender_user = ArgFromUser
    n.reciever_user = Arg2User

    n.content_type = Arg_ContentType
    n.object_id = Arg_ObjectID
    n.msg_notify_type = Arg_MSG_TYPE

    n.msg_txt = Arg_MsgTxt
    n.msg_url = Arg_Url
    n.save()

    # if users have a mail's
    if settings.EMAIL_HOST_USER and n.reciever_user.email:
        context_dict = { 'n' : n,
                         'current_domain' : get_full_site_url(),
                         'msg_txt' : decode_json2msg( Arg_MsgTxt ),
                         'domains' : Arg_Additional_Msg_Tags, }


        html_message_text = render_to_string( 'profiles/email_notification.txt', context_dict )

        #html_message_text = '<p><a href="' + Site.objects.get_current().domain + n.get_absolute_url() + '">' + decode_json2msg( Arg_MsgTxt ) + '</a></p>'
        #if Arg_Additional_Msg_Tags:
        #    arg_additional_msg = '<strong>Domains</strong>'
        #    for t in Arg_Additional_Msg_Tags:
        #        arg_additional_msg = arg_additional_msg + '<p>[' + t + ']</p>'
        #    html_message_text = html_message_text + '<hr>' + arg_additional_msg

        try:
            send_mail( decode_json2msg( Arg_MsgTxt ),
                       html_message_text,
                       settings.EMAIL_HOST_USER,
                       [n.reciever_user.email],
                       fail_silently=False,
                       html_message=html_message_text
                     )
        except:
            print( 'Fail to send email' )
