from django.contrib.auth.models import User, Permission

from django.test import TestCase, Client

from django.urls import reverse_lazy

from .models import Project, Task, Milestone, Get_Profiles_Available2Task, Get_Profile_Tasks, TaskCheckList, TaskLink, PROJECT_VISIBLE_PRIVATE, PROJECT_VISIBLE_VISIBLE, PROJECT_VISIBLE_OPEN, TASK_PROFILE_PRIORITY_RESPONSIBLE_FULL, TASK_PROFILE_PRIORITY_RESPONSIBLE_HOLDER, Sub_Project

from ich_bau.profiles.models import Profile, PROFILE_TYPE_RESOURCE, Profile_Manage_User

TEST_USER_NAME  = 'test_user'
TEST_USER_EMAIL = 'test_user@nothere.com'
TEST_USER_PW    = 'test_user_pw'

TEST_PROJECT_1_FULLNAME = 'TEST PROJECT #1 FULL NAME'
TEST_PROJECT_1_DESCRIPTION_1 = 'First version of description'

TEST_TASK_FULLNAME = 'TEST TASK #1 FULL NAME'

class Schedule_View_Test_Client(TestCase):
    def test_Schedule_All_Public(self):
        c = Client()
        response = c.get( reverse_lazy('project:view_my_index_schedule') )
        self.assertEqual(response.status_code, 302 )

        # create user
        if not User.objects.filter( username = TEST_USER_NAME ).exists():
            test_user = User.objects.create_user( username = TEST_USER_NAME, password = TEST_USER_PW )

        c = Client()

        # log in
        res = c.login( username = TEST_USER_NAME, password = TEST_USER_PW )
        self.assertTrue( res )

        response = c.get( reverse_lazy('project:view_my_index_schedule') )
        self.assertContains(response, 'Your schedule', status_code = 200 )
        self.assertContains(response, reverse_lazy('project:create_schedule_current'), status_code = 200 )

