from django.contrib.auth.models import User
from .models import *

from django.test import TestCase

BOT_TEST_NAME = 'BOT TEST NAME'

class Profile_Test(TestCase):
    def setUp(self):
        if not User.objects.filter( username = 'bot' ).exists():
            bot = User.objects.create_user( username = 'bot', password = '123' )
            bot_profile = bot.profile
            bot_profile.profile_type = PROFILE_TYPE_BOT
            bot_profile.name = BOT_TEST_NAME
            bot_profile.save()

    def test_Bot_profile_type(self):
        bot_profile = Profile.objects.get(name=BOT_TEST_NAME)
        self.assertEqual( bot_profile.profile_type, PROFILE_TYPE_BOT )

    def test_Bot_repo_pw(self):
        bot_profile = Profile.objects.get(name=BOT_TEST_NAME)
        self.assertFalse( bot_profile.repo_pw is None )

    def test_Bot_notifications_Zero(self):
        bot_profile = Profile.objects.get(name=BOT_TEST_NAME)
        self.assertEqual( GetUserNoticationsQ( bot_profile.user, True).count(), 0 )

from django.test import Client
class Profile_Test_Client(TestCase):
    def test_Profile_Test_Client_Root(self):
        c = Client()
        response = c.post( '/profile/view/' )
        self.assertEqual( response.status_code, 302 ) # we are not authorized - login redirect