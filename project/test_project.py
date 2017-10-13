#from django.contrib.auth.models import User
from .models import *

from django.test import TestCase

from django.db import transaction
import reversion
#from reversion.models import Version

TEST_USER_NAME_CREATOR = 'test project creator'
TEST_USER_NAME_NOT_MEMBER = 'user is not a member'
TEST_PROJECT_NAME = 'test project name'

def get_project():
    return Project.objects.get(fullname=TEST_PROJECT_NAME)

def get_creator_user():
    return User.objects.get( username = TEST_USER_NAME_CREATOR )

def get_user_not_member():
    return User.objects.get( username = TEST_USER_NAME_NOT_MEMBER )

class Project_Test(TestCase):
    def setUp(self):
        user_creator = User.objects.create_user( username = TEST_USER_NAME_CREATOR, password = '-' )
        user_creator.save()

        user_not_member = User.objects.create_user( username = TEST_USER_NAME_NOT_MEMBER, password = '-' )
        user_not_member.save()

        test_project = Project(fullname=TEST_PROJECT_NAME)
        test_project.set_change_user(user_creator)
        test_project.save()

    def test_have_repo_false(self):
        test_project = get_project()
        self.assertEqual( test_project.have_repo(), False )

    def test_creator_is_member(self):
        test_project = get_project()
        user_creator = get_creator_user()
        self.assertEqual( test_project.is_member(user_creator), True )

    def test_creator_is_member_False(self):
        test_project = get_project()
        user_not_member = get_user_not_member()
        self.assertEqual( test_project.is_member(user_not_member), False )

    def test_creator_is_member_None(self):
        test_project = get_project()        
        self.assertEqual( test_project.is_member(None), False )

    def test_creator_is_admin(self):
        test_project = get_project()
        user_creator = get_creator_user()
        self.assertEqual( test_project.is_admin(user_creator), True )

    def test_creator_can_admin(self):
        test_project = get_project()
        user_creator = get_creator_user()
        self.assertEqual( test_project.can_admin(user_creator), True )

    def test_creator_acl_admin(self):
        test_project = get_project()
        user_creator = get_creator_user()
        self.assertEqual( test_project.user_access_level(user_creator), PROJECT_ACCESS_ADMIN )

    def test_none_user_acl_admin(self):
        test_project = get_project()
        self.assertEqual( test_project.user_access_level( None ), PROJECT_ACCESS_VIEW )
