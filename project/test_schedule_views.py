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

class Project_View_Test_Client(TestCase):
    def test_Project_All_Public(self):
        c = Client()
        response = c.get( reverse_lazy('project:view_my_index_schedule') )
        self.assertEqual(response.status_code, 302 )
