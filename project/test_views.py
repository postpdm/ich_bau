from django.contrib.auth.models import User, Permission

from django.test import TestCase, Client

from django.urls import reverse_lazy

from .models import Project, Task, Milestone, Get_Profiles_Available2Task, Get_Profile_Tasks, TaskCheckList, TaskLink, PROJECT_VISIBLE_PRIVATE, PROJECT_VISIBLE_VISIBLE, PROJECT_VISIBLE_OPEN, TASK_PROFILE_PRIORITY_RESPONSIBLE_FULL, TASK_PROFILE_PRIORITY_RESPONSIBLE_HOLDER, Sub_Project

from ich_bau.profiles.models import Profile, PROFILE_TYPE_RESOURCE, Profile_Manage_User

TEST_USER_NAME  = 'test_user'
TEST_USER_EMAIL = 'test_user@nothere.com'
TEST_USER_PW    = 'test_user_pw'

TEST_PROJECT_FULLNAME = 'TEST PROJECT #1 FULL NAME'
TEST_PROJECT_DESCRIPTION_1 = 'First description'
TEST_PROJECT_DESCRIPTION_2 = 'Second description'

TEST_TASK_FULLNAME = 'TEST TASK #1 FULL NAME'

TEST_TASK_IN_MILESTONE_FULLNAME = 'TEST TASK #2 IN MILESTONE FULL NAME'

TEST_MILESTONE_FULLNAME = 'TEST MILESTONE #1 FULL NAME'
TEST_MILESTONE_FULLNAME_2 = 'TEST MILESTONE #1 NEW FULL NAME'

TASK_CHECK_CAPTION = 'Do it!'

TEST_SUB_PROJECT_FULLNAME         = 'TEST PROJECT #1 - SU PROJECT #1'
TEST_SUB_PROJECT_FULLNAME_CHANGED = 'TEST PROJECT #1 - SUB PROJECT #1'

class Project_View_Test_Client(TestCase):
    def test_Project_All_Public(self):
        c = Client()
        response = c.get( reverse_lazy('project:all_public') )
        self.assertEqual( response.status_code, 200 )

    def test_Project_All_Available(self):
        c = Client()
        response = c.get( reverse_lazy('project:all_available') )
        self.assertEqual( response.status_code, 200 )

    def test_Search_Project_Page_is_200(self):
        c = Client()
        response = c.get( reverse_lazy('project:search_public') )
        self.assertContains(response, '0 found.', status_code=200 )

    def test_Project_Index(self):
        c = Client()
        response = c.get( reverse_lazy('project:index') )
        self.assertContains(response, 'Please, log in to see your projects.', status_code=200 )

    def test_Long_Long(self):
        # no projects here
        self.assertEqual( Project.objects.count(), 0 )

        # create user
        if not User.objects.filter( username = TEST_USER_NAME ).exists():
            test_user = User.objects.create_user( username = TEST_USER_NAME, password = TEST_USER_PW )

        c = Client()
        # check for project search page is available for anon
        response = c.get( reverse_lazy('project:search_public'), { 'fullname' : TEST_PROJECT_FULLNAME } )
        self.assertContains(response, '0 found.', status_code=200 )

        # log in
        res = c.login( username = TEST_USER_NAME, password = TEST_USER_PW )
        self.assertTrue( res )

        # create new project with post
        response = c.post( reverse_lazy('project:project_add'), { 'fullname' : TEST_PROJECT_FULLNAME, 'description' : TEST_PROJECT_DESCRIPTION_1, } )

        # forbidden
        self.assertEqual( response.status_code, 403 )
        self.assertEqual( Project.objects.count(), 0 )

        # need to add the permissions
        add_project_permission = Permission.objects.get(codename='add_project')
        test_user.user_permissions.add( add_project_permission )

        response = c.post( reverse_lazy('project:project_add'), { 'fullname' : TEST_PROJECT_FULLNAME, 'private_type' : PROJECT_VISIBLE_VISIBLE, 'description' : TEST_PROJECT_DESCRIPTION_1, } )
        # we are redirected to new project page
        self.assertEqual( response.status_code, 302 )

        # check project is created
        self.assertEqual( Project.objects.count(), 1 )
        test_project_1 = Project.objects.get(id=1)
        self.assertEqual( response.url, test_project_1.get_absolute_url() )
        self.assertEqual( test_project_1.fullname, TEST_PROJECT_FULLNAME )
        self.assertEqual( test_project_1.description, TEST_PROJECT_DESCRIPTION_1 )
        self.assertTrue( test_project_1.is_member( test_user ) )

        # check - new project is available in search page
        response = c.get( reverse_lazy('project:search_public'), { 'fullname' : TEST_PROJECT_FULLNAME, 'description' : TEST_PROJECT_DESCRIPTION_1, } )
        self.assertContains(response, '1 found.', status_code=200 )

        response = c.get( reverse_lazy('project:search_public'), { 'fullname' : '-no-', 'description' : '-no-' } )
        self.assertContains(response, '0 found.', status_code=200 )

        # check - project page is available
        response = c.get( reverse_lazy('project:project_view', args = (test_project_1.id,) ) )
        self.assertContains(response, TEST_PROJECT_FULLNAME, status_code=200 )

        # check - project unknown is 404
        response = c.get( reverse_lazy('project:project_view', args = (9999999999,) ) )
        self.assertEqual(response.status_code, 404 )

        # check - project unknown page is 404
        response = c.get( reverse_lazy('project:project_view', args = (test_project_1.id,) ) + '/page_unknown' )
        self.assertEqual(response.status_code, 404 )

        # check - project history page is available
        response = c.get( reverse_lazy('project:project_history', args = (test_project_1.id,) ) )
        self.assertContains(response, TEST_PROJECT_FULLNAME, status_code=200 )

        # check - project milestone list page is available
        response = c.get( reverse_lazy('project:project_view_milestones', args = (test_project_1.id,) ) )
        self.assertContains(response, TEST_PROJECT_FULLNAME, status_code=200 )

        # check - project closed task list page is available
        response = c.get( reverse_lazy('project:project_view_closed_tasks', args = (test_project_1.id,) ) )
        self.assertContains(response, TEST_PROJECT_FULLNAME, status_code=200 )

        # check - project search task list page is available
        response = c.get( reverse_lazy('project:project_view_search_tasks', args = (test_project_1.id,) ) )
        self.assertContains(response, TEST_PROJECT_FULLNAME, status_code=200 )

        # check - project search view files page is available
        response = c.get( reverse_lazy('project:project_view_files', args = (test_project_1.id,) ) )
        self.assertContains(response, TEST_PROJECT_FULLNAME, status_code=200 )

        # https://github.com/postpdm/ich_bau/commit/fe1d5b55cf926e8b795598de0a40b4332b7f140c
        # check - try to create the repo for this project
        # response = c.get( reverse_lazy('project:project_create_repo', args = (test_project_1.id,) ),  follow=True )
        # self.assertRedirects(response, reverse_lazy('project:project_view_files', args = (test_project_1.id,) ) )

        # self.assertContains(response, TEST_PROJECT_FULLNAME, status_code=200 )
        # self.assertContains(response, "You successfully create the repo for this project!", status_code=200 )

        # check - try to create the repo for this project AGAIN - should print "already have!"
        # response = c.get( reverse_lazy('project:project_create_repo', args = (test_project_1.id,) ),  follow=True )
        # self.assertRedirects(response, reverse_lazy('project:project_view_files', args = (test_project_1.id,) ) )

        # self.assertContains(response, TEST_PROJECT_FULLNAME, status_code=200 )
        # self.assertContains(response, "Project already have a repo!", status_code=200 )

        # check form posting from edit page - set new description
        response = c.post( reverse_lazy('project:project_edit', args = (test_project_1.id,)), { 'fullname' : TEST_PROJECT_FULLNAME,
                           'private_type' : test_project_1.private_type, 'description' : TEST_PROJECT_DESCRIPTION_2, } )

        self.assertEqual(response.status_code, 302 )
        # refresh object from db
        test_project_1.refresh_from_db()
        # is description actually changed?
        self.assertEqual( test_project_1.description, TEST_PROJECT_DESCRIPTION_2 )

        response = c.get( reverse_lazy('project:search_public'), { 'fullname' : TEST_PROJECT_FULLNAME, 'description' : TEST_PROJECT_DESCRIPTION_1 } )
        self.assertContains(response, '0 found.', status_code=200 )
        response = c.get( reverse_lazy('project:search_public'), { 'fullname' : TEST_PROJECT_FULLNAME, 'description' : TEST_PROJECT_DESCRIPTION_2 } )
        self.assertContains(response, '1 found.', status_code=200 )

        self.assertEqual( Task.objects.count(), 0 )
        # create first task
        response = c.post( reverse_lazy('project:task_add', args = (test_project_1.id,) ), { 'fullname' : TEST_TASK_FULLNAME, } )
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

        # visit task page
        response = c.get( reverse_lazy('project:task_view', args = (test_task_1.id,) ) )
        self.assertContains(response, TEST_TASK_FULLNAME, status_code=200 )
        # visit task history page
        response = c.get( reverse_lazy('project:task_history', args = (test_task_1.id,) ) )
        self.assertContains(response, TEST_TASK_FULLNAME, status_code=200 )

        # Milestones

        self.assertEqual( Milestone.objects.count(), 0 )

        # create first milestone
        response = c.post( reverse_lazy('project:milestone_add', args = (test_project_1.id,) ), { 'fullname' : TEST_MILESTONE_FULLNAME, } )
        # we are redirected to new milestone page
        self.assertEqual( response.status_code, 302 )
        self.assertEqual( Milestone.objects.count(), 1 )

        test_ms_1 = Milestone.objects.get(id=1)
        # check url
        self.assertEqual( response.url, test_ms_1.get_absolute_url() )
        # check name
        self.assertEqual( test_ms_1.fullname, TEST_MILESTONE_FULLNAME )
        # check milestone is in project
        self.assertEqual( test_ms_1.project, test_project_1 )

        # visit milestone page
        response = c.get( reverse_lazy('project:milestone_view', args = (test_ms_1.id,) ) )
        self.assertContains(response, TEST_MILESTONE_FULLNAME, status_code=200 )
        # visit milestone history page
        response = c.get( reverse_lazy('project:milestone_history', args = (test_ms_1.id,) ) )
        self.assertContains(response, TEST_MILESTONE_FULLNAME, status_code=200 )

        # edit milestone

        response = c.post( reverse_lazy('project:milestone_edit', args = (test_ms_1.id,) ), { 'fullname' : TEST_MILESTONE_FULLNAME_2, } )
        # we are redirected to edited milestone page
        self.assertEqual( response.status_code, 302 )
        self.assertEqual( Milestone.objects.count(), 1 )
        test_ms_1.refresh_from_db()
        self.assertEqual( test_ms_1.fullname, TEST_MILESTONE_FULLNAME_2 )

        # task_checklist
        response = c.get( reverse_lazy('project:task_checklist', args = (0,) ) )
        self.assertEqual( response.status_code, 404 )

        # create task from milestone
        response = c.post( reverse_lazy('project:task_add_to_milestone', args = (test_ms_1.id, ) ), { 'fullname' : TEST_TASK_IN_MILESTONE_FULLNAME, 'milestone' : test_ms_1.id } )
        # we are redirected to new task page
        self.assertEqual( response.status_code, 302 )

        test_task_2 = Task.objects.get(fullname=TEST_TASK_IN_MILESTONE_FULLNAME)
        self.assertEqual( test_task_2.milestone.id, test_ms_1.id )

        # profiles
        avail_profiles = Get_Profiles_Available2Task( test_task_2.id )

        self.assertEqual( avail_profiles.count(), 1 )
        self.assertEqual( avail_profiles.filter( user = test_user ).count(), 1 )

        self.assertEqual( test_task_2.get_profiles().count(), 0 )

        new_resource = Profile( profile_type = PROFILE_TYPE_RESOURCE, name = 'Resource' )
        new_resource.save()
        self.assertEqual( avail_profiles.count(), 2 )
        self.assertEqual( Get_Profile_Tasks( new_resource ).count(), 0 )

        response = c.post( reverse_lazy('project:add_profile', args = (test_task_2.id, ) ), { 'profile' : new_resource.id, 'priority' : TASK_PROFILE_PRIORITY_RESPONSIBLE_FULL, } )
        # we are redirected to new task page
        self.assertEqual( response.status_code, 302 )

        self.assertEqual( test_task_2.get_profiles().count(), 1 )
        self.assertEqual( avail_profiles.count(), 1 )
        profile_assigned = test_task_2.get_profiles().first()
        self.assertEqual( profile_assigned.get_priority_caption(), 'Full responsible' )
        self.assertEqual( profile_assigned.get_allowed_priority(), ( (0, 'Interested'), (2, 'Holder'), (3, 'Executant') ) )

        self.assertEqual( Get_Profile_Tasks( new_resource ).count(), 1 )

        response = c.post( reverse_lazy('project:switch_assign_responsibillty', args = (profile_assigned.id, TASK_PROFILE_PRIORITY_RESPONSIBLE_HOLDER ) ) )
        # we are redirected to task page
        self.assertEqual( response.status_code, 302 )
        profile_assigned.refresh_from_db()
        self.assertEqual( profile_assigned.get_priority_caption(), 'Holder' )
        self.assertEqual( profile_assigned.get_allowed_priority(), ( (0, 'Interested'), (1, 'Full responsible'), (3, 'Executant') ) )

        response = c.get( reverse_lazy('profiles_detail', args = (new_resource.id, ) ) )
        # can't see the Task in Resource profile - becouse Resource is not managed by test user
        self.assertContains(response, test_task_2.fullname, status_code=200 )
        self.assertContains(response, 'Projects and tasks assigned to profile (for projects available for you)', status_code=200 )

        response = c.get( reverse_lazy('profiles_detail', args = (new_resource.id, ) ) )
        # can't see the Task in Resource profile - becouse Resource is not managed by test user
        self.assertContains(response, test_task_2.fullname, status_code=200 )

        # add control from test_user above new_resource
        npmu = Profile_Manage_User( manager_user = test_user, managed_profile = new_resource )
        npmu.save()

        response = c.get( reverse_lazy('profiles_detail', args = (new_resource.id, ) ) )
        # Now can see the Task in Resource profile - becouse Resource is now managed by test user
        self.assertContains(response, test_task_2.fullname, status_code=200 )
        self.assertContains(response, 'Projects and tasks assigned to managed profiles', status_code=200 )

        # task check list
        # test wrong task id
        response = c.post( reverse_lazy('project:task_checklist', args = (0, ) ) )
        self.assertEqual( response.status_code, 404 )

        # test check list is empty
        self.assertEqual( TaskCheckList.objects.filter( parenttask = test_task_2  ).count(), 0 )

        # create one item in the check list
        response = c.post( reverse_lazy('project:task_checklist', args = (test_task_2.id, ) ),
            { 'form-TOTAL_FORMS': 3,
              'form-INITIAL_FORMS': 0 ,
              'form-0-checkname' : TASK_CHECK_CAPTION, } )

        self.assertEqual( response.status_code, 302 )

        self.assertEqual( TaskCheckList.objects.filter( parenttask = test_task_2 ).count(), 1 )
        checks = TaskCheckList.objects.filter( parenttask = test_task_2  )
        self.assertEqual( checks.first().checkname, TASK_CHECK_CAPTION )
        self.assertFalse( checks.first().check_flag )

        # switch check item

        check_item = checks.first()
        check_item.refresh_from_db()
        self.assertEqual( check_item.checkname, TASK_CHECK_CAPTION )
        self.assertFalse( check_item.check_flag )
        response = c.get( reverse_lazy('project:task_check_switch', args = (check_item.id, ) ) )
        check_item.refresh_from_db()
        self.assertEqual( check_item.checkname, TASK_CHECK_CAPTION )
        self.assertTrue( check_item.check_flag )

        # add_linked

        self.assertEqual( TaskLink.objects.filter( maintask = test_task_1 ).count(), 0 )
        self.assertEqual( TaskLink.objects.filter( maintask = test_task_2 ).count(), 0 )

        response = c.post( reverse_lazy('project:add_linked', args = (test_task_1.id, ) ) + '?project=' + str( test_project_1.pk ), { 'subtasks' : test_task_2.id }, )

        self.assertEqual( response.status_code, 302 )

        self.assertEqual( TaskLink.objects.filter( maintask = test_task_1 ).count(), 1 )
        self.assertEqual( TaskLink.objects.filter( maintask = test_task_2 ).count(), 0 )

        # task_unlink

        # wrong link id raise 404
        response = c.post( reverse_lazy('project:task_unlink', args = (0, ) ) )
        self.assertEqual( response.status_code, 404 )

        # unlink previously created link
        response = c.post( reverse_lazy('project:task_unlink', args = (TaskLink.objects.first().id, ) ) )
        self.assertEqual( response.status_code, 302 )
        self.assertEqual( TaskLink.objects.filter( maintask = test_task_1 ).count(), 0 )
        self.assertEqual( TaskLink.objects.filter( maintask = test_task_2 ).count(), 0 )

        # test domains

        # wrong link id raise 404
        response = c.post( reverse_lazy('project:project_task_domain_unlink', args = (0, ) ) )
        self.assertEqual( response.status_code, 404 )


        # test report
        response = c.post( reverse_lazy('project:project_view_report_all_tasks', args = (test_project_1.id, ) ) )
        self.assertEqual( response.status_code, 200 )

        self.assertContains(response, test_task_1.fullname, status_code=200 )
        self.assertContains(response, test_task_2.fullname, status_code=200 )

    def test_sub_projects(self):
        # no projects here
        self.assertEqual( Project.objects.count(), 0 )

        # create user
        if not User.objects.filter( username = TEST_USER_NAME ).exists():
            test_user = User.objects.create_user( username = TEST_USER_NAME, password = TEST_USER_PW )

        c = Client()
        # log in
        res = c.login( username = TEST_USER_NAME, password = TEST_USER_PW )
        self.assertTrue( res )

        add_project_permission = Permission.objects.get(codename='add_project')
        test_user.user_permissions.add( add_project_permission )

        response = c.post( reverse_lazy('project:project_add'), { 'fullname' : TEST_PROJECT_FULLNAME, 'private_type' : PROJECT_VISIBLE_VISIBLE, 'description' : TEST_PROJECT_DESCRIPTION_1, } )
        # we are redirected to new project page
        self.assertEqual( response.status_code, 302 )

        # check project is created
        self.assertEqual( Project.objects.count(), 1 )
        test_project_1 = Project.objects.get(id=1)
        self.assertEqual( response.url, test_project_1.get_absolute_url() )
        self.assertEqual( test_project_1.fullname, TEST_PROJECT_FULLNAME )
        self.assertEqual( test_project_1.description, TEST_PROJECT_DESCRIPTION_1 )
        self.assertTrue( test_project_1.is_member( test_user ) )
        self.assertFalse( test_project_1.use_sub_projects )

        response = c.get( reverse_lazy('project:project_view', args = (test_project_1.id,) ) )
        # project doesn't contain SUB projects
        self.assertNotContains(response, 'Sub projects', status_code=200 )

        response = c.get( reverse_lazy('project:project_view_sub_projects', args = (test_project_1.id,) ) )
        self.assertEqual( response.status_code, 404 )

        response = c.post( reverse_lazy('project:project_edit', args = (test_project_1.id,)), { 'fullname' : TEST_PROJECT_FULLNAME, 'private_type' : PROJECT_VISIBLE_VISIBLE, 'use_sub_projects' : True, } )

        self.assertEqual(response.status_code, 302 )
        # refresh object from db
        test_project_1.refresh_from_db()
        # is use_sub_projects actually changed?
        self.assertTrue( test_project_1.use_sub_projects )

        response = c.get( reverse_lazy('project:project_view_sub_projects', args = (test_project_1.id,) ) )
        self.assertContains(response, 'Sub projects', count = 2, status_code=200 )

        response = c.post( reverse_lazy('project:sub_project_add', args = (test_project_1.id,)), { 'fullname' : TEST_SUB_PROJECT_FULLNAME, } )
        self.assertEqual(response.status_code, 302 )
        sub_project_1 = Sub_Project.objects.get(id=1)
        self.assertEqual( sub_project_1.project, test_project_1 )
        self.assertEqual( sub_project_1.fullname, TEST_SUB_PROJECT_FULLNAME )
        self.assertEqual( sub_project_1.get_absolute_url(), '/project/sub_project/1/' )

        response = c.get( reverse_lazy('project:sub_project_view', args = (sub_project_1.id,) ) )
        self.assertContains(response, TEST_SUB_PROJECT_FULLNAME, status_code=200 )


        response = c.post( reverse_lazy('project:sub_project_edit', args = (test_project_1.id,)), { 'fullname' : TEST_SUB_PROJECT_FULLNAME_CHANGED, } )
        self.assertEqual(response.status_code, 302 )
        sub_project_1.refresh_from_db()

        self.assertEqual( sub_project_1.fullname, TEST_SUB_PROJECT_FULLNAME_CHANGED )

        response = c.get( reverse_lazy('project:sub_project_view', args = (sub_project_1.id,) ) )
        self.assertContains(response, TEST_SUB_PROJECT_FULLNAME_CHANGED, status_code=200 )

        response = c.get( reverse_lazy('project:sub_project_history', args = (sub_project_1.id,) ) )
        self.assertContains(response, TEST_SUB_PROJECT_FULLNAME_CHANGED, status_code=200 )
        self.assertContains(response, TEST_SUB_PROJECT_FULLNAME, status_code=200 )

