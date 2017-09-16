from .models import Notification

def Send_Notification( ArgFromUser, Arg2User, Arg_MsgTxt, Arg_Url ):
    n = Notification()
    n.sender_user = ArgFromUser
    n.reciever_user = Arg2User
    n.msg_txt = Arg_MsgTxt
    n.msg_url = Arg_Url
    n.save()