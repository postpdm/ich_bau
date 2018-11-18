'''Test the project collaboration route. With views.'''
from django.contrib.auth.models import User

from django.test import TestCase, Client

from django.urls import reverse_lazy

from .models import Project, Task, Milestone

from ich_bau.profiles.models import GetUserNoticationsQ

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

class Project_Collaboration_View_Test_Client(TestCase):
    def test_Project_Collaboration(self):
        if not User.objects.filter( username = TEST_ADMIN_USER_NAME ).exists():
            test_admin_user = User.objects.create_user( username = TEST_ADMIN_USER_NAME, password = TEST_ADMIN_USER_PW )

        c_a = Client()
        response = c_a.login( username = TEST_ADMIN_USER_NAME, password = TEST_ADMIN_USER_PW )
        self.assertTrue( response )

        # create new project with post
        response = c_a.post( reverse_lazy('project:project_add'), { 'fullname' : TEST_PROJECT_FULLNAME, 'description' : TEST_PROJECT_DESCRIPTION_1, } )
        # we are redirected to new project page
        self.assertEqual( response.status_code, 302 )

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

        # check the notification
        notification = GetUserNoticationsQ( test_worker_user, True).first()
        self.assertEqual( notification.sender_user, test_admin_user)
        self.assertEqual( notification.reciever_user, test_worker_user)
        self.assertEqual( notification.msg_url, test_project_1.get_absolute_url() )

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

        response = c_sw.post( reverse_lazy('project:member_want_join', args = (test_project_1.id,)  ) )
        # we are redirected to project page
        self.assertEqual( response.status_code, 302 )
        # self worker is still not a member
        self.assertEqual( test_project_1.is_member(test_self_worker_user), False )
        # self worker get NO notification
        self.assertEqual( GetUserNoticationsQ( test_self_worker_user, True).count(), 0 )

        # check the notification

        