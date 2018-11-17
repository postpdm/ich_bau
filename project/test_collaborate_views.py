'''Test the project collaboration route. With views.'''
from django.contrib.auth.models import User

from django.test import TestCase, Client

from django.urls import reverse_lazy

from .models import Project, Task, Milestone

TEST_ADMIN_USER_NAME  = 'test_admin_user'
TEST_ADMIN_USER_EMAIL = 'test_admin_user@nothere.com'
TEST_ADMIN_USER_PW    = 'test_admin_user_pw'

TEST_WORKER_USER_NAME  = 'test_worker_user'
TEST_WORKER_USER_EMAIL = 'test_worker_user@nothere.com'
TEST_WORKER_USER_PW    = 'test_worker_user_pw'

TEST_PROJECT_FULLNAME = 'TEST PROJECT FOR COLLABORATION #1 FULL NAME'

TEST_TASK_FULLNAME = 'TEST TASK FOR COLLABORATION #1 FULL NAME'

TEST_PROJECT_DESCRIPTION_1 = 'Project for collaboration'

class Project_Collaboration_View_Test_Client(TestCase):
    def test_Project_Collaboration(self):
        if not User.objects.filter( username = TEST_ADMIN_USER_NAME ).exists():
            test_admin_user = User.objects.create_user( username = TEST_ADMIN_USER_NAME, password = TEST_ADMIN_USER_PW )

        c_a = Client()
        res = c_a.login( username = TEST_ADMIN_USER_NAME, password = TEST_ADMIN_USER_PW )
        self.assertTrue( res )

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

        #c_w = Client()
        #res = c_w.login( username = TEST_WORKER_USER_NAME, password = TEST_WORKER_USER_PW )
        #self.assertTrue( res )

        #response = c_a.post( reverse_lazy('project:member_add', args = (test_project_1.id,)  ), { } )
        # we are redirected to new project page
        #self.assertEqual( response.status_code, 302 )
