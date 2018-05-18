from django.contrib.auth.models import User
from .models import *

from django.test import TestCase, Client
from django.urls import reverse_lazy

BOT_TEST_NAME = 'BOT TEST NAME'

TEST_USER_NAME = 'USER'
TEST_USER_PW = 'USER_PW'

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

    def test_Bot_profile_absolute_url(self):
        bot_profile = Profile.objects.get(name=BOT_TEST_NAME)
        self.assertEqual( bot_profile.get_absolute_url(), '/p/1/' )

    def test_Bot_profile_page(self):
        bot_profile = Profile.objects.get(name=BOT_TEST_NAME)
        c = Client()
        response = c.get( bot_profile.get_absolute_url() )
        self.assertContains(response, BOT_TEST_NAME + ' (Bot)', status_code=200 )

    def test_Create_Wrong_profile_type(self):
        p = Profile( profile_type = -9999 )
        with self.assertRaises(Exception):
            p.save()

class Profile_Test_Client(TestCase):
    def setUp(self):
        if not User.objects.filter( username = 'bot' ).exists():
            bot = User.objects.create_user( username = 'bot', password = '123' )
            bot_profile = bot.profile
            bot_profile.profile_type = PROFILE_TYPE_BOT
            bot_profile.name = BOT_TEST_NAME
            bot_profile.save()

        if not User.objects.filter( username = TEST_USER_NAME ).exists():
            u = User.objects.create_user( username = TEST_USER_NAME, password = TEST_USER_PW )
            u.save()

    def test_Profile_Test_Client_Root(self):
        c = Client()
        response = c.post( '/profile/view/' )
        self.assertEqual( response.status_code, 302 ) # we are not authorized - login redirect

    def test_Profile_Test_Client_Root_Wrong_Login(self):
        c = Client()
        res = c.login(username='perfect_stranger', password='yaoyao!')
        self.assertFalse( res )

    def test_Profile_View_My_Profile(self):
        u = User.objects.all()

        c = Client()
        res = c.login(username=TEST_USER_NAME, password=TEST_USER_PW )
        self.assertTrue( res )

        response = c.get( reverse_lazy('my_profile_view'), follow=True )
        self.assertEqual( response.status_code, 200 )
