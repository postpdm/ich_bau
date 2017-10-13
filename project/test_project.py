#from django.contrib.auth.models import User
from .models import *

from django.test import TestCase

from django.db import transaction
import reversion
#from reversion.models import Version

TEST_USER_NAME_CREATOR = 'test project creator'
TEST_PROJECT_NAME = 'test project name'

def get_project():
    return Project.objects.get(fullname=TEST_PROJECT_NAME)

def get_creator_user():
    return User.objects.get( username = TEST_USER_NAME_CREATOR )

class Project_Test(TestCase):
    def setUp(self):
        user_creator = User.objects.create_user( username = TEST_USER_NAME_CREATOR, password = '-' )
        user_creator.save()

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

    def test_creator_is_admin(self):
        test_project = get_project()
        user_creator = get_creator_user()
        self.assertEqual( test_project.is_admin(user_creator), True )

    def test_creator_can_admin(self):
        test_project = get_project()
        user_creator = get_creator_user()
        self.assertEqual( test_project.can_admin(user_creator), True )
