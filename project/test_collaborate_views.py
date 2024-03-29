'''Test the project collaboration route. With views.'''
from django.contrib.auth.models import User, Permission

from django.test import TestCase, Client
from django.test.testcases import SimpleTestCase, TransactionTestCase

from django.urls import reverse_lazy

from .models import Project, Task, Milestone, TaskComment, GetTaskAssignedUser, TaskProfile, PROJECT_VISIBLE_PRIVATE, PROJECT_VISIBLE_VISIBLE, TASK_PROFILE_PRIORITY_RESPONSIBLE_FULL

from reversion.models import Version

from ich_bau.profiles.models import GetUserNoticationsQ

from .test_svn_wrapper_consts import get_TEST_REPO_SVN_FILE
import shutil, tempfile, os
from project.repo_wrapper import *

TEST_ADMIN_USER_NAME  = 'test_admin_user'
TEST_ADMIN_USER_EMAIL = 'test_admin_user@nothere.com'
TEST_ADMIN_USER_PW    = 'test_admin_user_pw'

TEST_WORKER_USER_NAME  = 'test_worker_user'
TEST_WORKER_USER_EMAIL = 'test_worker_user@nothere.com'
TEST_WORKER_USER_PW    = 'test_worker_user_pw'

TEST_SELF_WORKER_USER_NAME  = 'test_self_worker_user'
TEST_SELF_WORKER_USER_EMAIL = 'test_self_worker_user@nothere.com'
TEST_SELF_WORKER_USER_PW    = 'test_self_worker_user_pw'

TEST_PROJECT_FULLNAME = 'TEST PROJECT FOR COLLABORATION #1 FULL NAME'

TEST_TASK_FULLNAME = 'TEST TASK FOR COLLABORATION #1 FULL NAME'

TEST_PROJECT_DESCRIPTION_1 = 'Project for collaboration'

TEST_TASK_FIRST_COMMENT = 'Hloo!'
TEST_TASK_FIRST_COMMENT_2 = 'Hello!'

TEST_TASK_SECOND_COMMENT = 'I''m here!'

class Project_Collaboration_View_Test_Client(TestCase):
    def test_Project_Collaboration(self):
        if not User.objects.filter( username = TEST_ADMIN_USER_NAME ).exists():
            test_admin_user = User.objects.create_user( username = TEST_ADMIN_USER_NAME, password = TEST_ADMIN_USER_PW )

        c_a = Client()
        response = c_a.login( username = TEST_ADMIN_USER_NAME, password = TEST_ADMIN_USER_PW )
        self.assertTrue( response )

        self.assertEqual( Project.objects.count(), 0 )

        # create new project with post
        response = c_a.post( reverse_lazy('project:project_add'), { 'fullname' : TEST_PROJECT_FULLNAME, 'description' : TEST_PROJECT_DESCRIPTION_1, } )
        # forbidden
        self.assertEqual( response.status_code, 403 )
        self.assertEqual( Project.objects.count(), 0 )

        # need to add the permissions
        add_project_permission = Permission.objects.get(codename='add_project')
        test_admin_user.user_permissions.add( add_project_permission )

        # create new project with post
        response = c_a.post( reverse_lazy('project:project_add'), { 'fullname' : TEST_PROJECT_FULLNAME, 'private_type' : PROJECT_VISIBLE_PRIVATE, 'description' : TEST_PROJECT_DESCRIPTION_1, }, follow = True )

        # we are redirected to new project page
        self.assertContains(response, '<i class="fa fa-lock"></i>', status_code=200 )

        # check project is created
        self.assertEqual( Project.objects.count(), 1 )
        test_project_1 = Project.objects.get(id=1)

        self.assertEqual( test_project_1.is_member(test_admin_user), True )

        if not User.objects.filter( username = TEST_WORKER_USER_NAME ).exists():
            test_worker_user = User.objects.create_user( username = TEST_WORKER_USER_NAME, password = TEST_WORKER_USER_PW )

        self.assertEqual( test_project_1.is_member(test_worker_user), False )
        self.assertEqual( GetUserNoticationsQ( test_worker_user, True).count(), 0 )

        c_w = Client()
        response = c_w.login( username = TEST_WORKER_USER_NAME, password = TEST_WORKER_USER_PW )
        self.assertTrue( response )

        # add new user
        response = c_a.post( reverse_lazy('project:member_add', args = (test_project_1.id,)  ), { 'member_profile' : test_worker_user.profile.id } )
        # we are redirected to project page
        self.assertEqual( response.status_code, 302 )
        # worker is still not a member
        self.assertEqual( test_project_1.is_member(test_worker_user), False )
        # but worker get the notification
        self.assertEqual( GetUserNoticationsQ( test_worker_user, True).count(), 1 )

        response = c_w.get( reverse_lazy('unread_notifications_view' ) )
        self.assertContains(response, test_project_1.fullname, status_code=200 )
        response = c_w.get( reverse_lazy('unread_notifications_view_by_type' ) )
        self.assertContains(response, test_project_1.fullname, status_code=200 )

        # check the notification
        notification = GetUserNoticationsQ( test_worker_user, True).first()
        self.assertEqual( notification.sender_user, test_admin_user)
        self.assertEqual( notification.reciever_user, test_worker_user)
        self.assertEqual( notification.msg_url, reverse_lazy('project:project_view_members', kwargs={ 'project_id': test_project_1.id} ) )

        # visit the notification link
        response = c_w.get( reverse_lazy('notification_read', args = (notification.id,)  ) )
        self.assertEqual( response.status_code, 302 )
        self.assertEqual( GetUserNoticationsQ( test_worker_user, True).count(), 0 )

        # member record 0 should not exist
        response = c_w.get( reverse_lazy('project:member_accept', args = (0,)  ) )
        self.assertEqual( response.status_code, 404 )
        member_id = test_project_1.GetMemberList().get( member_profile = test_worker_user.profile ).id
        self.assertEqual( member_id, 2 )

        response = c_w.get( reverse_lazy('project:member_accept', args = (member_id,)  ) )
        self.assertEqual( response.status_code, 302 )

        self.assertEqual( test_project_1.is_member(test_worker_user), True )

        # new user want to join
        if not User.objects.filter( username = TEST_SELF_WORKER_USER_NAME ).exists():
            test_self_worker_user = User.objects.create_user( username = TEST_SELF_WORKER_USER_NAME, password = TEST_SELF_WORKER_USER_PW )

        self.assertEqual( test_project_1.is_member(test_self_worker_user), False )
        self.assertEqual( GetUserNoticationsQ( test_self_worker_user, True).count(), 0 )

        c_sw = Client()
        response = c_sw.login( username = TEST_SELF_WORKER_USER_NAME, password = TEST_SELF_WORKER_USER_PW )
        self.assertTrue( response )

        self.assertEqual( GetUserNoticationsQ( test_admin_user, True).count(), 0 )

        response = c_sw.post( reverse_lazy('project:member_want_join', args = (test_project_1.id,)  ) )
        # we are redirected to project page
        self.assertEqual( response.status_code, 302 )
        # self worker is still not a member
        self.assertEqual( test_project_1.is_member(test_self_worker_user), False )

        # self worker get NO notification
        self.assertEqual( GetUserNoticationsQ( test_self_worker_user, True).count(), 0 )
        # check the admin notification
        self.assertEqual( GetUserNoticationsQ( test_admin_user, True).count(), 1 )

        notification = GetUserNoticationsQ( test_admin_user, True).first()
        self.assertEqual( notification.sender_user, test_self_worker_user )
        self.assertEqual( notification.reciever_user, test_admin_user)
        self.assertEqual( notification.msg_url, test_project_1.get_absolute_url() )

        # visit the notification link
        response = c_a.get( reverse_lazy('notification_read', args = (notification.id,)  ) )
        self.assertEqual( response.status_code, 302 )
        self.assertEqual( GetUserNoticationsQ( test_admin_user, True).count(), 0 )

        # accept the self joined

        member_id = test_project_1.GetMemberList().get( member_profile = test_self_worker_user.profile ).id
        self.assertEqual( member_id, 3 )

        # try to accept new member from non admin user
        response = c_w.get( reverse_lazy('project:team_accept', args = (member_id,)  ) )
        # non admin user is not allowed to accept the members
        self.assertEqual( response.status_code, 403 )

        self.assertEqual( test_project_1.is_member(test_self_worker_user), False )

        # try to accept new member from  admin user
        response = c_a.get( reverse_lazy('project:team_accept', args = (member_id,)  ) )
        # admin user is  allowed to accept the members
        self.assertEqual( response.status_code, 302 )
        # done - self joined user is accpeted
        self.assertEqual( test_project_1.is_member(test_self_worker_user), True )

        # create first task
        self.assertEqual( Task.objects.count(), 0 )
        # create first task
        response = c_a.post( reverse_lazy('project:task_add', args = (test_project_1.id,) ), { 'fullname' : TEST_TASK_FULLNAME, } )
        # we are redirected to new task page
        self.assertEqual( response.status_code, 302 )

        self.assertEqual( Task.objects.count(), 1 )
        # get object
        test_task_1 = Task.objects.get(id=1)
        # check url
        self.assertEqual( response.url, test_task_1.get_absolute_url() )
        # check name
        self.assertEqual( test_task_1.fullname, TEST_TASK_FULLNAME )
        # check task is in project
        self.assertEqual( test_task_1.project, test_project_1 )
        # check task history
        response = c_a.get( reverse_lazy('project:task_history', args = (test_task_1.id,) ) )
        # check history records count
        self.assertContains(response, TEST_TASK_FULLNAME, status_code=200 )
        self.assertEqual( Version.objects.get_for_object( test_task_1 ).count(), 1 )

        # check the task comments count - 0
        self.assertEqual( test_task_1.get_comments().count(), 0 )

        # post new comments from admin to unexisted task
        response = c_a.post( reverse_lazy('project:task_view', args = (0,) ), { 'submit' : 'submit', 'comment' : 'sss' } )
        self.assertEqual( response.status_code, 404 ) # should fail

        # post new comments from admin
        response = c_a.post( reverse_lazy('project:task_view', args = (test_task_1.id,) ), { 'submit' : 'submit', 'comment' : TEST_TASK_FIRST_COMMENT } )
        self.assertEqual( response.status_code, 302 )
        self.assertEqual( test_task_1.get_comments().count(), 1 )

        comment_1 = test_task_1.get_comments().first()
        self.assertEqual( comment_1.comment, TEST_TASK_FIRST_COMMENT )
        self.assertEqual( Version.objects.get_for_object( comment_1 ).count(), 1 )

        # edit comment from another user
        response = c_w.post( reverse_lazy('project:edit_task_comment', args = (comment_1.id,) ), { 'submit' : 'submit', 'comment' : TEST_TASK_FIRST_COMMENT_2 } )
        self.assertEqual( response.status_code, 404 )
        # edit comment from author
        response = c_a.post( reverse_lazy('project:edit_task_comment', args = (comment_1.id,) ), { 'submit' : 'submit', 'comment' : TEST_TASK_FIRST_COMMENT_2 } )
        self.assertEqual( response.status_code, 302 )
        comment_1.refresh_from_db()
        self.assertEqual( comment_1.comment, TEST_TASK_FIRST_COMMENT_2 )
        self.assertEqual( Version.objects.get_for_object( comment_1 ).count(), 2 )

        # check comment history
        response = c_a.get( reverse_lazy('project:task_comment_history', args = (comment_1.id,) ) )
        self.assertContains(response, TEST_TASK_FIRST_COMMENT, status_code=200 )
        self.assertEqual( Version.objects.get_for_object( comment_1 ).count(), 2 )

        self.assertEqual( GetUserNoticationsQ( test_admin_user, True).count(), 0 )
        self.assertEqual( GetUserNoticationsQ( test_worker_user, True).count(), 0 )
        self.assertEqual( GetUserNoticationsQ( test_self_worker_user, True).count(), 0 )

        response = c_w.post( reverse_lazy('project:task_view', args = (test_task_1.id,) ), { 'submit' : 'submit', 'comment' : TEST_TASK_SECOND_COMMENT } )
        self.assertEqual( response.status_code, 302 )
        self.assertEqual( test_task_1.get_comments().count(), 2 )

        self.assertEqual( GetUserNoticationsQ( test_admin_user, True).count(), 1 )
        self.assertEqual( GetUserNoticationsQ( test_worker_user, True).count(), 0 )
        self.assertEqual( GetUserNoticationsQ( test_self_worker_user, True).count(), 0 )

        # visit the notification link
        notification = GetUserNoticationsQ( test_admin_user, True).first()
        response = c_a.get( reverse_lazy('notification_read', args = (notification.id,)  ) )
        self.assertEqual( response.status_code, 302 )
        self.assertEqual( GetUserNoticationsQ( test_admin_user, True).count(), 0 )

        # edit task
        self.assertEqual( Task.objects.count(), 1 )

        self.assertEqual( GetTaskAssignedUser(test_task_1).count(), 0 )

        response = c_a.post( reverse_lazy('project:add_user', args = (test_task_1.id,) ), { 'profile' : test_worker_user.profile.id, 'priority' : TASK_PROFILE_PRIORITY_RESPONSIBLE_FULL, } )
        # we are redirected to task page
        self.assertEqual( response.status_code, 302 )

        test_task_1.refresh_from_db()
        self.assertEqual( Task.objects.count(), 1 )

        assignee = GetTaskAssignedUser(test_task_1)
        self.assertEqual( assignee.count(), 1 )

        self.assertEqual( assignee.filter( profile = test_worker_user.profile ).count(), 1 )

        self.assertEqual( GetUserNoticationsQ( test_admin_user, True).count(), 0 )
        self.assertEqual( GetUserNoticationsQ( test_worker_user, True).count(), 1 )
        self.assertEqual( GetUserNoticationsQ( test_self_worker_user, True).count(), 0 )


class SVN_Repo_Client_Test(TransactionTestCase):
    test_temp_dir = None

    def setUp(self):
        # Create a temporary directory
        if not self.test_temp_dir:
            self.test_temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        if self.test_temp_dir:
            shutil.rmtree(self.test_temp_dir, True )
            self.test_temp_dir = None

    def test_SVN_repo_collaboration(self):
        # test repo creation
        path = os.path.join(self.test_temp_dir, '' )

        with self.settings( REPO_SVN = get_TEST_REPO_SVN_FILE( path ) ):
            self.assertTrue( settings.REPO_SVN.get('REPO_TYPE') == svn_file )
            # user not logged in - project_create_repo is not called
            c = Client()
            response = c.get( reverse_lazy('project:project_create_repo', args = (0,)  ) )
            self.assertEqual( response.status_code, 302 )

            if not User.objects.filter( username = TEST_ADMIN_USER_NAME ).exists():
                test_admin_user = User.objects.create_user( username = TEST_ADMIN_USER_NAME, password = TEST_ADMIN_USER_PW )

            c_a = Client()
            response = c_a.login( username = TEST_ADMIN_USER_NAME, password = TEST_ADMIN_USER_PW )
            self.assertTrue( response )

            response = c_a.post( reverse_lazy('project:project_add'), { 'fullname' : TEST_PROJECT_FULLNAME, 'description' : TEST_PROJECT_DESCRIPTION_1, } )

            # forbidden
            self.assertEqual( response.status_code, 403 )
            self.assertEqual( Project.objects.count(), 0 )

            # need to add the permissions
            add_project_permission = Permission.objects.get(codename='add_project')
            test_admin_user.user_permissions.add( add_project_permission )

            response = c_a.post( reverse_lazy('project:project_add'), { 'fullname' : TEST_PROJECT_FULLNAME, 'private_type' : PROJECT_VISIBLE_VISIBLE, 'description' : TEST_PROJECT_DESCRIPTION_1, } )
            # we are redirected to new project page
            self.assertEqual( response.status_code, 302 )

            # check project is created
            self.assertEqual( Project.objects.count(), 1 )
            test_project_1 = Project.objects.get(id=1)

            self.assertEqual( test_project_1.is_member(test_admin_user), True )

            response = c_a.get( reverse_lazy('project:project_create_repo', args = (0,)  ) )
            self.assertEqual( response.status_code, 404 )

            # check - project search view files page is available
            response = c.get( reverse_lazy('project:project_view_files', args = (test_project_1.id,) ) )
            self.assertContains(response, TEST_PROJECT_FULLNAME, status_code=200 )

            response = c_a.get( reverse_lazy('project:project_create_repo', args = (test_project_1.id,)  ) )
            self.assertEqual( response.status_code, 302 )
            test_project_1.refresh_from_db()
            self.assertTrue( test_project_1.have_repo() )

            # check - project search view files page is available
            response = c.get( reverse_lazy('project:project_view_files', args = (test_project_1.id,) ) )
            self.assertContains(response, TEST_PROJECT_FULLNAME, status_code=200 )

            response = c_a.get( reverse_lazy('project:project_view_file_commit_view', args = (test_project_1.id, 0, )  ) )
            self.assertEqual( response.status_code, 200 )

            # check - try to create repo for project already has one
            response = c_a.get( reverse_lazy('project:project_create_repo', args = (test_project_1.id,) ), follow = True )
            # https://stackoverflow.com/questions/16143149/django-testing-check-messages-for-a-view-that-redirects
            self.assertEqual( response.status_code, 200 )
            self.assertRedirects(response, test_project_1.get_absolute_url() + 'files/')
            msg = list(response.context.get('messages'))[0]
            self.assertEqual( msg.tags, "error" )
            self.assertEqual( msg.message, "Project already have a repo!" )
