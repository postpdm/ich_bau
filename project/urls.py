from django.conf.urls import url
from django.urls import path

from project import views

app_name = 'project'

urlpatterns = [

    url(r'^$', views.index, name='index'),
    url(r'^all_available/$', views.index_available, name='all_available'),
    url(r'^all_public/$', views.index_public, name='all_public'),
    url(r'^search_public/$', views.index_search_public, name='search_public'),
    url(r'^task_search/$', views.index_task_search, name='task_search'),
    url(r'^task_search_by_domain/$', views.index_task_search_by_domain, name='task_search_by_domain'),
    url(r'^task_search_by_domain/selected/(?P<domain_id>\w+)/$', views.index_task_search_by_domain, name='task_search_by_domain_selected'),

    url(r'^project_add/$', views.ProjectCreateView.as_view(), name='project_add'),
    url(r'^project/(?P<project_id>\w+)/project_edit/$', views.project_edit, name='project_edit'),

    url(r'^project/(?P<project_id>\w+)/$', views.project_view, name='project_view'),
    url(r'^project/(?P<project_id>\w+)/history/$', views.project_history, name='project_history'),
    url(r'^project/(?P<project_id>\w+)/closed_task/$', views.project_view_closed_tasks, name='project_view_closed_tasks'),
    url(r'^project/(?P<project_id>\w+)/assigned_task/$', views.project_view_assigned_tasks, name='project_view_assigned_tasks'),
    url(r'^project/(?P<project_id>\w+)/unassigned_task/$', views.project_view_unassigned_tasks, name='project_view_unassigned_tasks'),

    # django v.2 path
    path( 'project/<project_id>/task_by_domain/', views.project_view_task_by_domain, name='project_view_task_by_domain'),
    path( 'project/<project_id>/task_by_domain/<domain_id>/', views.project_view_task_by_domain, name='project_view_task_for_domain'),

    url(r'^project/(?P<project_id>\w+)/search_task/$', views.project_view_search_tasks, name='project_view_search_tasks'),

    url(r'^project/(?P<project_id>\w+)/last_actions/$', views.project_view_last_actions, name='project_view_last_actions'),
    url(r'^project/(?P<project_id>\w+)/sub_projects/$', views.project_view_sub_projects, name='project_view_sub_projects'),
    url(r'^project/(?P<project_id>\w+)/members/$', views.project_view_members, name='project_view_members'),
    url(r'^project/(?P<project_id>\w+)/milestones/$', views.project_view_milestones, name='project_view_milestones'),
    url(r'^project/(?P<project_id>\w+)/reports/$', views.project_view_reports, name='project_view_reports'),

    url(r'^project/(?P<project_id>\w+)/report_all_tasks/$', views.project_view_report_all_tasks, name='project_view_report_all_tasks'),
    url(r'^project/(?P<project_id>\w+)/report_all_tasks_xls/$', views.project_view_report_all_tasks_xls.as_view(), name='project_view_report_all_tasks_xls'),
    # repo urls
    url(r'^project/(?P<project_id>\w+)/files/$', views.project_view_files, name='project_view_files'),
    url(r'^project/(?P<project_id>\w+)/files/commit/(?P<rev_id>\w+)/$', views.project_view_file_commit_view, name='project_view_file_commit_view'),
    url(r'^project/(?P<project_id>\w+)/create_repo/$', views.project_create_repo, name='project_create_repo'),

    url(r'^member_add/(?P<project_id>\w+)/$', views.AddMemberCreateView.as_view(), name='member_add'),
    url(r'^member_want_join/(?P<project_id>\w+)/$', views.member_want_join, name='member_want_join'),
    url(r'^member/(?P<member_id>\w+)/member_accept/$', views.member_accept, name='member_accept'),
    url(r'^member/(?P<member_id>\w+)/team_accept/$', views.team_accept, name='team_accept'),
    url(r'^member/(?P<member_id>\w+)/remove_check/$', views.member_remove_check, name='member_remove_check'),
    url(r'^member/(?P<member_id>\w+)/remove_confirm/$', views.member_remove_confirm, name='member_remove_confirm'),

    url(r'^task_add/(?P<project_id>\w+)/$', views.TaskCreateView.as_view(), name='task_add'),
    url(r'^task_add_to_milestone/(?P<milestone_id>\w+)/$', views.TaskCreateView.as_view(), name='task_add_to_milestone'),
    url(r'^task/(?P<pk>\w+)/edit/$', views.TaskUpdateView.as_view(), name='task_edit'),
    url(r'^task/(?P<task_id>\w+)/checklist/$', views.task_checklist, name='task_checklist'),
    url(r'^task/(?P<task_id>\w+)/$', views.task_view, name='task_view'),
    url(r'^task/(?P<task_id>\w+)/history/$', views.task_history, name='task_history'),
    url(r'^add_linked/(?P<task_id>\w+)/$', views.add_linked, name='add_linked'),

    url(r'^task/(?P<task_id>\w+)/add_property/$', views.task_add_property, name='task_add_property'),
    url(r'^task/(?P<task_property_id>\w+)/edit_property/$', views.task_edit_property, name='task_edit_property'),

    url(r'^sub_project_add/(?P<project_id>\w+)/$', views.Sub_ProjectCreateView.as_view(), name='sub_project_add'),
    url(r'^sub_project/(?P<sub_project_id>\w+)/$', views.sub_project_view, name='sub_project_view'),
    url(r'^sub_project/(?P<pk>\w+)/edit/$', views.Sub_ProjectUpdateView.as_view(), name='sub_project_edit'),
    url(r'^sub_project/(?P<sub_project_id>\w+)/history/$', views.sub_project_history, name='sub_project_history'),

    url(r'^task_move2project_dialog/(?P<task_id>\w+)/$', views.task_move2project, name='task_move2project_dialog'),
    url(r'^task_move2project_check/(?P<task_id>\w+)/target_project/(?P<project_id>\w+)/$', views.task_move2project, name='task_move2project_check'),

    url(r'^add_profile/(?P<task_id>\w+)/$', views.add_profile, name='add_profile'),
    url(r'^add_profile/(?P<task_id>\w+)/level/(?P<level_pk>\w+)/$', views.add_profile, name='add_profile_sub_tree_view'),
    url(r'^add_user/(?P<task_id>\w+)/$', views.add_user, name='add_user'),
    url(r'^switch_assign_responsibillty/(?P<taskprofile_id>\w+)/priority/(?P<priority_int>\w+)/$', views.switch_assign_responsibillty, name='switch_assign_responsibillty'),
    url(r'^remove_assign_responsibillty/(?P<taskprofile_id>\w+)/$', views.remove_assign_responsibillty, name='remove_assign_responsibillty'),

    url(r'^add_domain/(?P<task_id>\w+)/$', views.add_domain, name='add_domain'),

    url(r'^task_link/(?P<tasklink_id>\w+)/unlink/$', views.task_unlink, name='task_unlink'),

    path( 'task_domain/<taskdomain_id>/unlink', views.project_task_domain_unlink, name='project_task_domain_unlink'),

    url(r'^task_comment/(?P<task_comment_id>\w+)/edit/$', views.edit_task_comment, name='edit_task_comment'),
    url(r'^task_comment/(?P<task_comment_id>\w+)/history/$', views.task_comment_history, name='task_comment_history'),

    url(r'^task_check/(?P<task_check_id>\w+)/switch/$', views.task_check_switch, name='task_check_switch'),

    url(r'^milestone_add/(?P<project_id>\w+)/$', views.MilestoneCreateView.as_view(), name='milestone_add'),
    url(r'^milestone/(?P<pk>\w+)/edit/$', views.MilestoneUpdateView.as_view(), name='milestone_edit'),
    url(r'^milestone/(?P<milestone_id>\w+)/$', views.milestone_view, name='milestone_view'),
    url(r'^milestone/(?P<milestone_id>\w+)/history/$', views.milestone_history, name='milestone_history'),

    url(r'^schedule/view_my_index/$', views.view_my_schedule, name='view_my_index_schedule'),
    url(r'^schedule/view_profile_index/(?P<profile_id>\w+)/$', views.view_profile_schedule, name='view_profile_schedule'),
    url(r'^schedule_add_current/$', views.create_schedule_current, name='create_schedule_current'),
    url(r'^schedule_add_current/(?P<profile_id>\w+)/$', views.create_schedule_current, name='create_schedule_current'),
    url(r'^schedule_add_next/$', views.create_schedule_next, name='create_schedule_next'),
    url(r'^schedule_add_next/(?P<profile_id>\w+)/$', views.create_schedule_next, name='create_schedule_next'),
    url(r'^schedule/(?P<schedule_item_id>\w+)/$', views.schedule_item_view, name='schedule_item_view'),

    url(r'^schedule/(?P<schedule_item_id>\w+)/schedule_one_task/(?P<task_id>\w+)$', views.schedule_one_task, name='schedule_one_task'),
    url(r'^schedule/(?P<schedule_item_id>\w+)/unschedule_one_task/(?P<task_id>\w+)$', views.unschedule_one_task, name='unschedule_one_task'),

    ]