from django.contrib.auth.models import AnonymousUser
from .models import *

from django.test import TestCase

from django.db import transaction

import reversion

TEST_USER_NAME_CREATOR = 'test project creator'
TEST_USER_NAME_NOT_MEMBER = 'user is not a member'
TEST_PROJECT_PUBLIC_NAME = 'test project name public'
TEST_PROJECT_PRIVATE_NAME = 'test project name private'
TEST_PROJECT_TASK_FULLNAME        = 'Test project task'
TEST_PROJECT_TASK_DESCRIPTION = '<strong>A</strong>'

def get_public_project():
    return Project.objects.get(fullname=TEST_PROJECT_PUBLIC_NAME)

def get_private_project():
    return Project.objects.get(fullname=TEST_PROJECT_PRIVATE_NAME)

def get_creator_user():
    return User.objects.get( username = TEST_USER_NAME_CREATOR )

def get_user_not_member():
    return User.objects.get( username = TEST_USER_NAME_NOT_MEMBER )

def create_task():
    test_project = get_public_project()
    user_creator = get_creator_user()
    task = Task( project=test_project, fullname=TEST_PROJECT_TASK_FULLNAME, description = TEST_PROJECT_TASK_DESCRIPTION )
    task.set_change_user(user_creator)
    task.save()
    return task

class Project_Test(TestCase):
    def setUp(self):
        user_creator = User.objects.create_user( username = TEST_USER_NAME_CREATOR, password = '-' )
        user_creator.save()

        user_not_member = User.objects.create_user( username = TEST_USER_NAME_NOT_MEMBER, password = '-' )
        user_not_member.save()

        test_project_public = Project(fullname=TEST_PROJECT_PUBLIC_NAME)
        test_project_public.set_change_user(user_creator)
        test_project_public.private_type = PROJECT_VISIBLE_VISIBLE
        test_project_public.save()

        test_project_private = Project(fullname=TEST_PROJECT_PRIVATE_NAME)
        test_project_private.set_change_user(user_creator)
        test_project_private.private_type = PROJECT_VISIBLE_PRIVATE
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

    def test_anon_is_NOT_admin(self):
        test_project = get_public_project()
        user_anon = AnonymousUser()
        self.assertEqual( test_project.is_admin(user_anon), False )

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

    def test_GetFullMemberAdminList_public(self):
        self.assertEqual( get_public_project().GetFullMemberAdminList().count(), 1 )

    def test_member_User_can_join_public( self ):
        self.assertEqual( get_public_project().can_join( get_creator_user() ), False )

    def test_member_User_can_join_private( self ):
        self.assertEqual( get_private_project().can_join( get_creator_user() ), False )

    def test_not_member_User_can_join_public( self ):
        self.assertEqual( get_public_project().can_join( get_user_not_member() ), True )

    def test_not_member_User_can_join_private( self ):
        self.assertEqual( get_private_project().can_join( get_user_not_member() ), False )

    def test_Create_Task_check_fullname( self ):
        test_task = create_task()
        self.assertEqual( test_task.fullname, TEST_PROJECT_TASK_FULLNAME )

    def test_Create_Task_check_state( self ):
        test_task = create_task()
        self.assertEqual( test_task.state, TASK_STATE_NEW )

    def test_Create_Task_check_Description( self ):
        test_task = create_task()
        self.assertEqual( test_task.description_html(), TEST_PROJECT_TASK_DESCRIPTION )

    def test_task_Add_Comment( self ):
        test_task = create_task()
        user_creator = get_creator_user()
        c = TaskComment( parenttask = test_task, comment='123' )
        c.set_change_user(user_creator)
        c.save()
        self.assertEqual( c.comment, '123' )

        self.assertEqual( GetTaskCommentators( test_task ).count(), 1 )

        self.assertEqual( GetTaskCommentators( test_task, user_creator ).count(), 0 )

    def test_Task_Set_Wrong_State( self ):
        test_task = create_task()

        with self.assertRaises(Exception):
            test_task.set_task_state( get_creator_user(), -10202 ) # some imposible state

    def test_Task_Set_Closed_State( self ):
        test_task = create_task()

        test_task.set_task_state( get_creator_user(), TASK_STATE_CLOSED )
        self.assertEqual( test_task.state, TASK_STATE_CLOSED )
        self.assertFalse( test_task.get_opened() )
        self.assertEqual( test_task.get_state_name(), 'Closed' )

        self.assertIsNotNone( test_task.finished_fact_at )
        test_task.set_task_state( get_creator_user(), TASK_STATE_NEW )
        self.assertEqual( test_task.state, TASK_STATE_NEW )
        self.assertIsNone( test_task.finished_fact_at )
        self.assertTrue( test_task.get_opened() )
        self.assertEqual( test_task.get_state_name(), 'New' )

    def test_assignee( self ):
        t = Get_User_Tasks( None )
        self.assertEqual( t.count(), 0 )
        test_task = create_task()
        self.assertEqual( test_task.get_profiles().count(), 0 )
        tp = TaskProfile( parenttask = test_task, profile = get_creator_user().profile )
        tp.set_change_user( get_creator_user() )

        for p in TASK_PROFILE_PRIORITY_LIST:
            tp.priority = p
            tp.save()
            self.assertEqual( tp.priority, p )

        with self.assertRaises(Exception):
            tp.priority = max( TASK_PROFILE_PRIORITY_LIST ) + 1
            tp.save()

    def test_linked_resource(self):
        test_task = create_task()
        self.assertEqual( test_task.get_profiles().count(), 0 ) # new task has no profiles linked

        p = Get_Profiles_Available2Task( test_task.id )
        self.assertEqual( p.count(), 1 ) # 1 profile is available
        self.assertEqual( p.filter( user = get_creator_user() ).count(), 1 ) # creator_user profile is available

    def test_sub_project_default_false(self):
        test_project = get_public_project()
        self.assertEqual( test_project.use_sub_projects, False )

class Project_Set_Wrong_Private_Type_Test(TestCase):

    def test_Project_Set_Wrong_Private_Type( self ):
        user_creator = User.objects.create_user( username = TEST_USER_NAME_CREATOR, password = '-' )
        user_creator.save()

        user_not_member = User.objects.create_user( username = TEST_USER_NAME_NOT_MEMBER, password = '-' )
        user_not_member.save()

        with self.assertRaises(Exception):
            test_project_public = Project(fullname=TEST_PROJECT_PUBLIC_NAME)
            test_project_public.set_change_user(user_creator)
            test_project_public.private_type = -1111
            test_project_public.save()
