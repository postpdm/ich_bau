#from django.contrib.auth.models import User
from .models import *

from django.test import TestCase

from django.db import transaction
import reversion
#from reversion.models import Version

TEST_USER_NAME_CREATOR = 'test project creator'
TEST_USER_NAME_NOT_MEMBER = 'user is not a member'
TEST_PROJECT_PUBLIC_NAME = 'test project name public'
TEST_PROJECT_PRIVATE_NAME = 'test project name private'

def get_public_project():
    return Project.objects.get(fullname=TEST_PROJECT_PUBLIC_NAME)

def get_private_project():
    return Project.objects.get(fullname=TEST_PROJECT_PRIVATE_NAME)

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

        test_project_public = Project(fullname=TEST_PROJECT_PUBLIC_NAME)
        test_project_public.set_change_user(user_creator)
        test_project_public.save()

        test_project_private = Project(fullname=TEST_PROJECT_PRIVATE_NAME)
        test_project_private.set_change_user(user_creator)
        test_project_private.private_flag = True
        test_project_private.save()

    def test_have_repo_false(self):
        test_project = get_public_project()
        self.assertEqual( test_project.have_repo(), False )

    def test_creator_is_member(self):
        test_project = get_public_project()
        user_creator = get_creator_user()
        self.assertEqual( test_project.is_member(user_creator), True )

    def test_not_member_is_member_False(self):
        test_project = get_public_project()
        user_not_member = get_user_not_member()
        self.assertEqual( test_project.is_member(user_not_member), False )

    def test_creator_is_member_None(self):
        test_project = get_public_project()
        self.assertEqual( test_project.is_member(None), False )

    def test_creator_is_admin(self):
        test_project = get_public_project()
        user_creator = get_creator_user()
        self.assertEqual( test_project.is_admin(user_creator), True )

    def test_creator_can_admin(self):
        test_project = get_public_project()
        user_creator = get_creator_user()
        self.assertEqual( test_project.can_admin(user_creator), True )

    def test_creator_acl_admin(self):
        test_project = get_public_project()
        user_creator = get_creator_user()
        self.assertEqual( test_project.user_access_level(user_creator), PROJECT_ACCESS_ADMIN )

    def test_none_user_acl_admin_public(self):
        test_project = get_public_project()
        self.assertEqual( test_project.user_access_level( None ), PROJECT_ACCESS_VIEW )

    def test_none_user_acl_admin_private(self):
        test_project = get_private_project()
        self.assertEqual( test_project.user_access_level( None ), PROJECT_ACCESS_NONE )

    def test_public_project_list(self):
        pl = GetAllPublicProjectList()
        self.assertEqual( get_public_project() in pl, True )
        self.assertEqual( pl.count(), 1 )

    def test_GetMemberedProjectList_None(self):
        self.assertEqual( GetMemberedProjectList( None ), {} )

    def test_GetMemberedProjectList_NotMember(self):
        self.assertEqual( GetMemberedProjectList( get_user_not_member() ).count(), 0 )

    def test_GetMemberedProjectList_Creator(self):
        self.assertEqual( GetMemberedProjectList( get_creator_user() ).count(), 2 )