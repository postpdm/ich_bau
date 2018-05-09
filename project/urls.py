from django.conf.urls import url

from project import views

urlpatterns = [

    url(r'^$', views.index, name='index'),
    url(r'^all_public/$', views.index_public, name='all_public'),
    url(r'^search_public/$', views.index_search_public, name='search_public'),

    url(r'^project_add/$', views.ProjectCreateView.as_view(), name='project_add'),
    url(r'^project/(?P<project_id>\w+)/project_edit/$', views.project_edit, name='project_edit'),

    url(r'^project/(?P<project_id>\w+)/$', views.project_view, name='project_view'),
    url(r'^project/(?P<project_id>\w+)/history/$', views.project_history, name='project_history'),
    url(r'^project/(?P<project_id>\w+)/closed_task/$', views.project_view_closed_tasks, name='project_view_closed_tasks'),
    url(r'^project/(?P<project_id>\w+)/search_task/$', views.project_view_search_tasks, name='project_view_search_tasks'),
    url(r'^project/(?P<project_id>\w+)/milestones/$', views.project_view_milestones, name='project_view_milestones'),
    # repo urls
    url(r'^project/(?P<project_id>\w+)/files/$', views.project_view_files, name='project_view_files'),
    url(r'^project/(?P<project_id>\w+)/files/commit/(?P<rev_id>\w+)/$', views.project_view_file_commit_view, name='project_view_file_commit_view'),
    url(r'^project/(?P<project_id>\w+)/create_repo/$', views.project_create_repo, name='project_create_repo'),

    url(r'^member_add/(?P<project_id>\w+)/$', views.AddMemberCreateView.as_view(), name='member_add'),
    url(r'^member_want_join/(?P<project_id>\w+)/$', views.member_want_join, name='member_want_join'),
    url(r'^member/(?P<member_id>\w+)/member_accept/$', views.member_accept, name='member_accept'),
    url(r'^member/(?P<member_id>\w+)/team_accept/$', views.team_accept, name='team_accept'),

    url(r'^task_add/(?P<project_id>\w+)/$', views.TaskCreateView.as_view(), name='task_add'),
    url(r'^task_add_to_milestone/(?P<milestone_id>\w+)/$', views.TaskCreateView.as_view(), name='task_add_to_milestone'),
    url(r'^task/(?P<pk>\w+)/edit/$', views.TaskUpdateView.as_view(), name='task_edit'),
    url(r'^task/(?P<pk>\w+)/edit_target_date/$', views.edit_task_target_date, name='edit_task_target_date'),
    url(r'^task/(?P<task_id>\w+)/checklist/$', views.task_checklist, name='task_checklist'),
    url(r'^task/(?P<task_id>\w+)/$', views.task_view, name='task_view'),
    url(r'^task/(?P<task_id>\w+)/history/$', views.task_history, name='task_history'),
    url(r'^add_linked/(?P<task_id>\w+)/$', views.add_linked, name='add_linked'),

    url(r'^task_link/(?P<tasklink_id>\w+)/unlink/$', views.task_unlink, name='task_unlink'),


    url(r'^task_comment/(?P<task_comment_id>\w+)/edit/$', views.edit_task_comment, name='edit_task_comment'),
    url(r'^task_comment/(?P<task_comment_id>\w+)/history/$', views.task_comment_history, name='task_comment_history'),

    url(r'^task_check/(?P<task_check_id>\w+)/switch/$', views.task_check_switch, name='task_check_switch'),

    url(r'^milestone_add/(?P<project_id>\w+)/$', views.MilestoneCreateView.as_view(), name='milestone_add'),
    url(r'^milestone/(?P<pk>\w+)/edit/$', views.MilestoneUpdateView.as_view(), name='milestone_edit'),
    url(r'^milestone/(?P<milestone_id>\w+)/$', views.milestone_view, name='milestone_view'),
    url(r'^milestone/(?P<milestone_id>\w+)/history/$', views.milestone_history, name='milestone_history'),

    ]