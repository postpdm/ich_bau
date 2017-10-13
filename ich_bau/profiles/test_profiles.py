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