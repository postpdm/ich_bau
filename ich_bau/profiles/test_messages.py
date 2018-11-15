from django.contrib.auth.models import User
from .models import *

from django.test import TestCase
from .messages import *

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

