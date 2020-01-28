from django.contrib.auth.models import User
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from .models import *
from .messages import *
from .notification_helper import *

TEST_USER_NAME = 'USER'
TEST_USER_PW = 'USER_PW'

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

    def test_Send_Notification(self):
        test_user = User.objects.create_user( username = TEST_USER_NAME, password = TEST_USER_PW )
        self.assertEqual( GetUserNoticationsQ( test_user, True).count(), 0 )

        user_type = ContentType.objects.get(app_label='auth', model='user')

        Send_Notification( test_user, test_user, user_type, 1, MSG_NOTIFY_TYPE_USER_WANT_JOIN_ID, 'Arg_MsgTxt', 'Arg_Url' )
        self.assertEqual( GetUserNoticationsQ( test_user, True).count(), 1 )
