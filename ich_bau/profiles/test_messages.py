from django.contrib.auth.models import User
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from .models import *
from .messages import *
from .notification_helper import *

from django.conf import settings
from django.core import mail

TEST_USER_NAME = 'USER'
TEST_USER_PW = 'USER_PW'
TEST_USER_EMAIL = 'email@mail.mail'

SERVER_EMAIL = 'server@mail.mail'

class Message_Test(TestCase):
    def test_Encode_Decode_Project_MSG(self):
        s = project_msg2json_str( MSG_NOTIFY_TYPE_PROJECT_CHANGED_ID, arg_project_name = 'some project' )
        self.assertEqual( s, '{"msg_type": 20, "project_name": "some project"}' )
        self.assertEqual( decode_json2msg(s), "Changes in the 'some project' project." )

    def test_Encode_Project_MSG_Fail(self):
        s = project_msg2json_str( -1, arg_project_name = '*' )
        self.assertFalse( s )

    def test_Get_Users_Profiles(self):
        self.assertEqual( Get_Users_Profiles().count(), 0 )
        test_user = User.objects.create_user( username = TEST_USER_NAME, password = TEST_USER_PW )
        self.assertEqual( Get_Users_Profiles().count(), 1 )

    def test_Send_Notification_Wrong_Arg_MSG_TYPE(self):
        test_user = User.objects.create_user( username = TEST_USER_NAME, password = TEST_USER_PW )
        self.assertEqual( GetUserNoticationsQ( test_user, True).count(), 0 )

        user_type = ContentType.objects.get(app_label='auth', model='user')

        with self.assertRaises(Exception):
            Send_Notification( test_user, test_user, user_type, 1, -1, 'Arg_MsgTxt', 'Arg_Url' ) # try to raise 'Wrong message type'

    def test_Send_Notification(self):
        test_user = User.objects.create_user( username = TEST_USER_NAME, password = TEST_USER_PW )
        self.assertEqual( GetUserNoticationsQ( test_user, True).count(), 0 )

        user_type = ContentType.objects.get(app_label='auth', model='user')

        Send_Notification( test_user, test_user, user_type, 1, MSG_NOTIFY_TYPE_USER_WANT_JOIN_ID, 'Arg_MsgTxt', 'Arg_Url' )
        self.assertEqual( GetUserNoticationsQ( test_user, True).count(), 1 )

    def test_Send_Notification_Check_Email_ASK_ACCEPT(self):

        mail.outbox = []
        self.assertEqual(len(mail.outbox), 0)

        settings.EMAIL_HOST_USER = SERVER_EMAIL

        test_user = User.objects.create_user( username = TEST_USER_NAME, password = TEST_USER_PW, email = TEST_USER_EMAIL )
        self.assertEqual( GetUserNoticationsQ( test_user, True).count(), 0 )

        user_type = ContentType.objects.get(app_label='auth', model='user')

        msg_str = project_msg2json_str( MSG_NOTIFY_TYPE_ASK_ACCEPT_ID, arg_project_name = 'test' )
        self.assertEqual( msg_str, '{"msg_type": 1, "project_name": "test"}' )

        Send_Notification( test_user, test_user, user_type, 1, MSG_NOTIFY_TYPE_ASK_ACCEPT_ID, msg_str, 'Arg_Url' )
        self.assertEqual( GetUserNoticationsQ( test_user, True).count(), 1 )
        self.assertEqual(len(mail.outbox), 1)

        e_letter = mail.outbox[0]

        self.assertEqual( e_letter.from_email, SERVER_EMAIL )
        self.assertIn( TEST_USER_EMAIL, e_letter.to )
        self.assertEqual( e_letter.subject, 'You are asked to accept the membership of \'test\' project team!' )

        self.assertIn( 'You are asked to accept the membership of &#39;test&#39; project team!', e_letter.body )
