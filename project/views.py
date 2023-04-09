﻿from project.models import *
from project.forms import ProjectForm, TaskForm, TaskCommentForm, MilestoneForm, MemberForm, TaskLinkedForm, TaskProfileForm, TaskCheckListForm, TaskDomainForm, Sub_ProjectForm, Task_Property_Amount_Form
from ich_bau.profiles.models import Get_Users_Profiles, Close_All_Unread_Notifications_For_Task_For_One_User, Is_User_Manager, Get_Profiles_From_Level, PROFILE_TYPE_FOR_TREE
from django.forms.models import modelformset_factory
from django.urls import reverse
from django.db.models import Count

from django.http import HttpResponseForbidden, HttpResponse

from django.utils.html import strip_tags
from django.utils.encoding import escape_uri_path
from django.utils import timezone

from account.mixins import LoginRequiredMixin
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType

# Create your views here.

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, Http404
from django.views import generic
from django.contrib import messages

from django.template import RequestContext

#from django.contrib.auth.decorators import login_required
from account.decorators import login_required
from account.utils import handle_redirect_to_login
from django.contrib.auth import REDIRECT_FIELD_NAME

from django.db import transaction
import reversion
from reversion.models import Version

from project.filters import ProjectFilter, BaseTaskFilter, TaskFilter, TaskFilter_for_Linking

from project.repo_wrapper import *

# константы фильров по проектам
PROJECT_FILTER_MINE = 0
PROJECT_FILTER_SEARCH_PUBLIC = 1
PROJECT_FILTER_ALL_PUBLIC = 2
PROJECT_FILTER_ALL_AVAILABLE = 4
PROJECT_TASK_SEARCH = 5
PROJECT_TASK_SEARCH_BY_DOMAIN = 6

def get_index( request, arg_page = PROJECT_FILTER_MINE, arg_domain_id = None ):
    # Получить контекст из HTTP запроса.
    context = RequestContext(request)
    if arg_page == PROJECT_FILTER_MINE:
        my_task = None
        if request.user.is_authenticated:
            my_task = Get_User_Tasks(request.user)
        context_dict = { 'projects': GetMemberedProjectList(request.user),
                         'filter_type' : '',
                         'tasks' : my_task,
                         }
    else:
        if arg_page == PROJECT_FILTER_SEARCH_PUBLIC:
            filter = ProjectFilter(request.GET, queryset=GetAllPublicProjectList() )
            context_dict = { 'filter_type' : 'search_public', 'filter': filter }
        else:
            if arg_page == PROJECT_FILTER_ALL_PUBLIC:
                context_dict = {'projects': GetAllPublicProjectList(), 'filter_type' : 'all_public' }
            else:
                if arg_page == PROJECT_FILTER_ALL_AVAILABLE:
                    context_dict = {'projects': GetAvailableProjectList(request.user), 'filter_type' : 'all_available' }
                else:
                    if arg_page == PROJECT_TASK_SEARCH:
                        task_filter = BaseTaskFilter( request.GET, queryset=Task.objects.filter( project__in = GetAvailableProjectList(request.user) ) )
                        p_list = Get_Users_Profiles()
                        task_filter.filters['holder'].queryset = p_list

                        if task_filter.Search_is_new():
                            tasks = None
                        else:
                            tasks = task_filter.qs

                        context_dict = { 'projects': None, 'filter_type' : 'task_search',
                                         'filter': task_filter,
                                         'tasks' : tasks,
                        }
                    else:
                        if arg_page == PROJECT_TASK_SEARCH_BY_DOMAIN:
                            if arg_domain_id:
                                tasks = Task.objects.filter( task2domain__taskdomain = arg_domain_id )
                                selected_domain = int(arg_domain_id)
                            else:
                                # without domains
                                tasks = Task.objects.filter( task2domain__taskdomain = None )
                                selected_domain = None

                            domains = TaskDomain.objects.all()

                            context_dict = { 'projects': None, 'filter_type' : 'task_search_by_domain',
                                             'domains' : domains,
                                             'selected_domain' : selected_domain,
                                             #'filter': task_filter,
                                             'tasks' : tasks,
                            }
                        else:
                            raise Http404()

    # check if user has permission to create project (or super user)
    context_dict[ 'can_add_project' ] = request.user.has_perm('project.add_project')

    # Сформировать ответ, отправить пользователю
    return render( request, 'project/index.html', context_dict )

def index( request ):
    return get_index( request )

def index_search_public( request ):
    return get_index( request, PROJECT_FILTER_SEARCH_PUBLIC )

def index_available( request ):
    return get_index( request, PROJECT_FILTER_ALL_AVAILABLE )

def index_public( request ):
    return get_index( request, PROJECT_FILTER_ALL_PUBLIC )

def index_task_search( request ):
    return get_index( request, PROJECT_TASK_SEARCH )

def index_task_search_by_domain( request, domain_id = None ):
    return get_index( request, PROJECT_TASK_SEARCH_BY_DOMAIN, arg_domain_id = domain_id )

class ProjectCreateView( LoginRequiredMixin, PermissionRequiredMixin, CreateView):

    form_class = ProjectForm
    model = Project
    permission_required = 'project.add_project'

    raise_exception = True

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.set_change_user(self.request.user)

        with transaction.atomic(), reversion.create_revision():
            reversion.set_user(self.request.user)
            self.object.save()

        messages.success(self.request, "You successfully create the project!")
        return HttpResponseRedirect(self.get_success_url())

@login_required
def project_edit(request, project_id):
    context = RequestContext(request)

    project = get_object_or_404( Project, pk=project_id )

    if not project.can_admin( request.user ):
        raise Http404()

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            project.set_change_user(request.user)
            with transaction.atomic(), reversion.create_revision():
                reversion.set_user(request.user)
                form.save()

            # перебросить пользователя на просмотр изделия
            messages.success(request, "You successfully updated this project!")
            return HttpResponseRedirect( project.get_absolute_url() )
        else:
            print( form.errors )
    else:
        form = ProjectForm( instance=project )

    return render(  request, 'project/project_form.html',
            {'form': form, 'project':project},
             context)

# константы - фильтры по задачам
TASK_FILTER_OPEN = 0
TASK_FILTER_CLOSED = 1
TASK_FILTER_BY_DOMAIN = 2
TASK_FILTER_SEARCH = 3
TASK_FILTER_ASSIGNED = 4
TASK_FILTER_UNASSIGNED = 5

# Закладки страницы Проекта
PROJECT_PAGE_TITLE = 0
PROJECT_PAGE_MEMBERS = 5
PROJECT_PAGE_LAST_ACTIONS = 8
PROJECT_PAGE_SUB_PROJECTS = 9
PROJECT_PAGE_FILES = 10
PROJECT_PAGE_MILESTONES = 15
PROJECT_PAGE_REPORTS = 25

# Для передачи в шаблон
PROJECT_PAGE_FILTER = {
  PROJECT_PAGE_TITLE : 'title',
  PROJECT_PAGE_MEMBERS : 'members',
  PROJECT_PAGE_LAST_ACTIONS : 'last_actions',
  PROJECT_PAGE_SUB_PROJECTS : 'sub_projects',
  PROJECT_PAGE_FILES : 'files',
  PROJECT_PAGE_MILESTONES : 'milestones' ,
  PROJECT_PAGE_REPORTS : 'reports' ,
}

def project_view(request, project_id):
    return get_project_view(request, project_id )

def project_view_closed_tasks(request, project_id):
    return get_project_view(request, project_id, arg_task_filter = TASK_FILTER_CLOSED)

def project_view_assigned_tasks(request, project_id):
    return get_project_view(request, project_id, arg_task_filter = TASK_FILTER_ASSIGNED)

def project_view_unassigned_tasks(request, project_id):
    return get_project_view(request, project_id, arg_task_filter = TASK_FILTER_UNASSIGNED)

def project_view_task_by_domain(request, project_id, domain_id = None ):
    return get_project_view(request, project_id, arg_task_filter = TASK_FILTER_BY_DOMAIN, arg_domain_id = domain_id )

def project_view_search_tasks(request, project_id):
    return get_project_view(request, project_id, arg_task_filter = TASK_FILTER_SEARCH )

def project_view_last_actions(request, project_id):
    return get_project_view(request, project_id, arg_page = PROJECT_PAGE_LAST_ACTIONS )

def project_view_sub_projects(request, project_id):
    return get_project_view(request, project_id, arg_page = PROJECT_PAGE_SUB_PROJECTS )

def project_view_milestones(request, project_id):
    return get_project_view(request, project_id, arg_page = PROJECT_PAGE_MILESTONES )

def project_view_members(request, project_id):
    return get_project_view(request, project_id, arg_page = PROJECT_PAGE_MEMBERS )

def project_view_files(request, project_id):
    return get_project_view(request, project_id, arg_page = PROJECT_PAGE_FILES )

def project_view_reports(request, project_id):
    return get_project_view(request, project_id, arg_page = PROJECT_PAGE_REPORTS )

def project_history(request, project_id):
    context = RequestContext(request)
    project = get_object_or_404( Project, pk=project_id)

    ual = project.user_access_level( request.user )
    if ual == PROJECT_ACCESS_NONE:
        raise Http404()

    versions = Version.objects.get_for_object( project )

    context_dict = { 'project': project,
                     'versions': versions }
    # Рендерить ответ
    return render( request, 'project/project_history.html', context_dict )

@login_required
def project_create_repo(request, project_id):
    context = RequestContext(request)
    project = get_object_or_404( Project, pk=project_id)

    if project.have_repo():
        messages.error( request, "Project already have a repo!")
        return HttpResponseRedirect( project.get_absolute_url() + 'files' )

    ual = project.user_access_level( request.user )
    if ual == PROJECT_ACCESS_NONE:
        raise Http404()
    else:
        if ( ual == PROJECT_ACCESS_WORK ) or ( ual == PROJECT_ACCESS_VIEW ):
            messages.warning( request, "You have no admin rights for this project!")
            return HttpResponseRedirect( project.get_absolute_url() + 'files' )
        else:
            if ual == PROJECT_ACCESS_ADMIN:
                # create the repo
                res = Create_New_Repo()
                if res[0] == VCS_REPO_SUCCESS:
                    project.repo_name = res[1]
                    project.save()
                    # add access
                    project.add_repo_access()
                    messages.success( request, "You successfully create the repo for this project!")
                else:
                    messages.error( request, "Fail create the repo for this project!")
                return HttpResponseRedirect( project.get_absolute_url() + 'files' )
            else:
                raise Http404() # хотя такого быть не должно

def get_last_action_content( arg_project ):
    def mySort(e):
        return e['modified_at']

    depth = 10
    res = []
    comments = TaskComment.objects.filter( parenttask__project = arg_project ).order_by('-modified_at')[:depth]
    for c in comments:
        res.append( { 'modified_at' : c.modified_at, 'type' : 'comment', 'modified_user' : c.modified_user, 'title' : c.comment, 'url' : c.parenttask.get_absolute_url, 'url_title' : c.parenttask, } )

    tasks = Task.objects.filter( project = arg_project ).order_by('-modified_at')[:depth]
    for t in tasks:
        res.append( { 'modified_at' : t.modified_at, 'type' : 'task', 'modified_user' : t.modified_user, 'title' : t.fullname, 'url' : t.get_absolute_url, 'url_title' : t, } )

    res.sort(reverse=True, key=mySort)

    return res

def get_project_view(request, project_id, arg_task_filter = TASK_FILTER_OPEN, arg_page = PROJECT_PAGE_TITLE, arg_domain_id = None ):
    # Получить контекст запроса
    context = RequestContext(request)
    project = get_object_or_404( Project, pk=project_id)

    user_can_work = False
    user_can_admin = False
    user_can_join = False

    show_file_page = VCS_Configured()

    ual = project.user_access_level( request.user )
    if ual == PROJECT_ACCESS_NONE:
        # если пользователь не авторизован, то доступ только к открытым проектам и только на просмотр
        if ( request.user is None ) or ( not request.user.is_authenticated ):
            return handle_redirect_to_login( request, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None )
        else:
            raise Http404()
    else:
        if ual == PROJECT_ACCESS_WORK:
            user_can_work = True
        else:
            if ual == PROJECT_ACCESS_ADMIN:
                user_can_work = True
                user_can_admin = True

    user_can_join = project.can_join(request.user)

    milestones = None
    repo_info = None
    repo_list = None
    repo_server_is_configured = False
    members = None
    filter_type = ''
    task_filter = None
    tasks = None
    show_assignee_flag = None
    repo_rel_path = None
    domains = None
    selected_domain = None
    last_actions = None
    sub_projects = None
    open_tasks_without_subproject = None

    if arg_page == PROJECT_PAGE_MILESTONES:
        milestones = Get_Milestone_Report_for_Project(project)

    if arg_page == PROJECT_PAGE_FILES:
        if VCS_Configured():
            repo_server_is_configured = True
            # относительный путь - какую папку смотрим
            repo_rel_path = request.GET.get( 'path', '' )

            if project.have_repo():
                s = project.repo_name
                res_info = Get_Info_For_Repo_Name( s, settings.REPO_SVN.get('SVN_ADMIN_USER'), settings.REPO_SVN.get('SVN_ADMIN_PASSWORD') )
                if res_info[0] == VCS_REPO_SUCCESS:
                    repo_info = res_info[1]
                    res_list = Get_List_For_Repo_Name( s, repo_rel_path, settings.REPO_SVN.get('SVN_ADMIN_USER'), settings.REPO_SVN.get('SVN_ADMIN_PASSWORD' ) )
                    if res_list[0] == VCS_REPO_SUCCESS:
                        repo_list = res_list[1]
                    # после обращения - добавим / для построения списка нижележащих путей
                    if repo_rel_path:
                        repo_rel_path = repo_rel_path + '/'
                else:
                    messages.error( request, "Can't connect to repo!")
        else:
            messages.error( request, "Repo server is not configured!")

    # prepare tasks only for title page
    if arg_page == PROJECT_PAGE_TITLE:
        base_tasks = project.Get_Tasks()

        if arg_task_filter == TASK_FILTER_OPEN:
            tasks = base_tasks.filter( state = TASK_STATE_NEW )
        else:
            if arg_task_filter == TASK_FILTER_CLOSED:
                filter_type = 'filter_task_closed'
                tasks = base_tasks.filter( state = TASK_STATE_CLOSED )
            else:
                if arg_task_filter == TASK_FILTER_SEARCH:
                    filter_type = 'filter_task_search'
                    task_filter = TaskFilter( request.GET, queryset=base_tasks )
                    task_filter.filters['milestone'].queryset = Milestone.objects.filter( project = project )
                    p_list = project.GetFullMemberProfiles()
                    task_filter.filters['holder'].queryset = p_list
                    if task_filter.Search_is_new():
                        tasks = None
                    else:
                        tasks = task_filter.qs
                else:
                    if arg_task_filter == TASK_FILTER_BY_DOMAIN:
                        filter_type = 'filter_task_by_domain'
                        if arg_domain_id:
                            tasks = base_tasks.filter( task2domain__taskdomain = arg_domain_id )
                            selected_domain = int(arg_domain_id)
                        else:
                            # without domains
                            tasks = base_tasks.filter( task2domain__taskdomain = None )
                            selected_domain = None
                        domains = TaskDomain.objects.all()
                    else:
                        if arg_task_filter == TASK_FILTER_ASSIGNED:
                            filter_type = 'filter_task_assigned'
                            show_assignee_flag = True
                            print( show_assignee_flag)
                            tasks = base_tasks.filter( state = TASK_STATE_NEW ).filter( profile2task__priority__in = TASK_PROFILE_PRIORITY_ASSIGNED_LIST ).distinct()
                        else:
                            if arg_task_filter == TASK_FILTER_UNASSIGNED:
                                filter_type = 'filter_task_unassigned'
                                tasks = base_tasks.filter( state = TASK_STATE_NEW ).exclude( profile2task__priority__in = TASK_PROFILE_PRIORITY_ASSIGNED_LIST )
                            else:
                                raise Http404

    if arg_page == PROJECT_PAGE_MEMBERS:
        members = project.GetMemberList()

    if arg_page == PROJECT_PAGE_LAST_ACTIONS:
        last_actions = get_last_action_content( project )

    if arg_page == PROJECT_PAGE_SUB_PROJECTS:
        if project.use_sub_projects:
            sub_projects = Sub_Project.objects.filter( project = project )
            open_tasks_without_subproject = project.Get_Tasks().filter( state = TASK_STATE_NEW ).filter( sub_project__isnull = True )
        else:
            raise Http404

    if arg_page == PROJECT_PAGE_REPORTS:
        pass

    # Записать список в словарь
    context_dict = { 'project': project,
                     'members':members,
                     'milestones' : milestones,
                     'tasks' : tasks,
                     'show_assignee_flag' : show_assignee_flag,
                     'filter': task_filter,
                     'filter_type' : filter_type,
                     'user_can_work' : user_can_work,
                     'user_can_join' : user_can_join,
                     'user_can_admin' : user_can_admin,
                     'show_page' : PROJECT_PAGE_FILTER[arg_page],
                     'repo_server_is_configured' : repo_server_is_configured,
                     'repo_info' : repo_info,
                     'repo_list' : repo_list,
                     'repo_rel_path' : repo_rel_path,
                     'show_file_page' : show_file_page,
                     'domains' : domains,
                     'selected_domain' : selected_domain,
                     'last_actions' : last_actions,
                     'sub_projects' : sub_projects,
                     'open_tasks_without_subproject' : open_tasks_without_subproject,
                         }

    # Рендерить ответ
    return render( request, 'project/project.html', context_dict )

def project_view_report_all_tasks(request, project_id ):
    context = RequestContext(request)
    project = get_object_or_404( Project, pk=project_id)

    if not project.can_view( request.user ):
        raise Http404()

    context_dict = { 'tasks' : project.project2tasks.all().order_by('created_at'), 'project' : project }

    return render( request, 'project/project_report_all_tasks.html',
                   context_dict )

class project_view_report_all_tasks_xls(View):

    def get(self, request, project_id):
        context = RequestContext(request)
        project = get_object_or_404( Project, pk=project_id)

        if not project.can_view( request.user ):
            raise Http404()

        import io
        import xlsxwriter

        # Create an in-memory output file for the new workbook.
        output = io.BytesIO()

        # Even though the final file will be in memory the module uses temp
        # files during assembly for efficiency. To avoid this on servers that
        # don't allow temp files, for example the Google APP Engine, set the
        # 'in_memory' Workbook() constructor option as shown in the docs.
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # Get data to write to the spreadsheet.
        data = project.project2tasks.all().order_by('created_at')

        # Write data.
        fields = ( 'id', 'created_at', 'fullname', 'holder', 'state', 'detailed_state', 'milestone', 'finished_fact_at', 'important', 'kind', 'sub_project' )

        # linked properties titles
        prop_fields = None
        if project.use_properties:
            tpt = Task_Property_Type.objects.all()
            prop_fields = {}
            for p in tpt:
                prop_fields[p.id] = p.name

        row_num = 0
        col_num = 0
        for field in fields:
            title = Task._meta.get_field( field ).verbose_name
            worksheet.write(row_num, col_num, title)
            col_num = col_num + 1
        if prop_fields:
            for pf in prop_fields:
                title = prop_fields[ pf ]
                worksheet.write(row_num, col_num, title)
                col_num = col_num + 1

        row_num = 1
        for task in data:
            col_num = 0
            for field in fields:
                cell_data = getattr(task, field )
                if cell_data:
                    worksheet.write(row_num, col_num, str( cell_data) )
                col_num = col_num + 1

            if prop_fields:
                for pf in prop_fields:
                    try:
                        a = Task_Property_Amount.objects.get( task=task, property_id = pf )
                        cell_data = a.amount
                        if a.amount:
                            worksheet.write(row_num, col_num, str( cell_data) )
                    except:
                        pass
                    col_num = col_num + 1
            row_num = row_num + 1

        worksheet.autofilter(0, 0, 1, col_num - 1 )  # set the filter

        # Close the workbook before sending the data.
        workbook.close()

        # Rewind the buffer.
        output.seek(0)

        # Set up the Http response.
        n = timezone.now()
        filename = project_id + '_' + project.fullname + '_' + str( n ) + '.xlsx'

        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = "attachment; filename=%s" % escape_uri_path(filename)
        return response

def project_view_file_commit_view(request, project_id, rev_id):
    context = RequestContext(request)
    project = get_object_or_404( Project, pk=project_id)

    rev_info = None

    if VCS_Configured():
        repo_server_is_configured = True

        if project.have_repo():
            s = project.repo_name
            try:
                res_info = Get_Log_For_Repo_Name( s, settings.REPO_SVN.get('SVN_ADMIN_USER'), settings.REPO_SVN.get('SVN_ADMIN_PASSWORD'), rev_num=rev_id )
                if res_info[0] == VCS_REPO_SUCCESS:
                    rev_info = res_info[1][0]
                else:
                    messages.error( request, "Wrong revision id or some error!")
            except:
                messages.error( request, "Wrong revision id or some error!")
        else:
            messages.error( request, "Can't connect to repo!")
    else:
        messages.error( request, "Repo server is not configured!")

    context_dict = { 'project': project,
                     'rev_id' : rev_id,
                     'rev_info' : rev_info,
    }
    return render( request, 'project/project_repo_commit.html', context_dict )

class MilestoneCreateView(LoginRequiredMixin, CreateView):

    form_class = MilestoneForm
    model = Milestone

    def form_valid(self, form):
        if 'project_id' in self.kwargs:
            project_id = self.kwargs['project_id']
        else:
            raise Http404()

        self.object = form.save(commit=False)
        self.object.set_change_user(self.request.user)
        if not ( project_id is None ):
            p = get_object_or_404( Project, pk = project_id )
            self.object.project = p

        with transaction.atomic(), reversion.create_revision():
            reversion.set_user(self.request.user)
            self.object.save()

        messages.success(self.request, "You successfully create the milestone!")
        return HttpResponseRedirect(self.get_success_url())

class MilestoneUpdateView(LoginRequiredMixin, UpdateView):
    form_class = MilestoneForm
    model = Milestone

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.set_change_user(self.request.user)
        with transaction.atomic(), reversion.create_revision():
            reversion.set_user(self.request.user)
            self.object.save()

        messages.success(self.request, "You successfully update the milestone!")
        return HttpResponseRedirect(self.get_success_url())

def milestone_history(request, milestone_id):
    # Получить контекст запроса
    context = RequestContext(request)

    milestone = get_object_or_404( Milestone, pk=milestone_id)

    versions = Version.objects.get_for_object( milestone )

    # Записать список в словарь
    context_dict = { 'milestone': milestone,
                     'versions': versions }

    # Рендерить ответ
    return render( request, 'project/milestone_history.html', context_dict )

def milestone_view(request, milestone_id):
    # Получить контекст запроса
    context = RequestContext(request)

    milestone = get_object_or_404( Milestone, pk=milestone_id)

    ual = milestone.project.user_access_level( request.user )
    user_can_work = False
    user_can_admin = False
    if ual == PROJECT_ACCESS_NONE:
        raise Http404()
    else:
        if ual == PROJECT_ACCESS_WORK:
            user_can_work = True
        else:
            if ual == PROJECT_ACCESS_ADMIN:
                user_can_work = True
                user_can_admin = True

    tasks = Task.objects.filter( milestone = milestone ).order_by('state')

    # Записать список в словарь
    context_dict = { 'milestone': milestone,
                     'tasks' : tasks,
                     'user_can_admin' : user_can_admin,
                     'user_can_work' : user_can_work,
                         }

    # Рендерить ответ
    return render( request, 'project/milestone.html', context_dict )

class AddMemberCreateView(LoginRequiredMixin, CreateView):
    form_class = MemberForm
    model = Member

    def get_initial(self):
        self.p = get_object_or_404( Project, pk = self.kwargs['project_id'])
        return { 'project': self.p, }

    def form_valid(self, form):
        if 'project_id' in self.kwargs:
            project_id = self.kwargs['project_id']
        else:
            raise Http404()

        self.object = form.save(commit=False)
        self.object.set_change_user(self.request.user)
        self.object.set_team_accept()
        if not ( project_id is None ):
            p = get_object_or_404( Project, pk = project_id )
            self.object.project = p

        #with transaction.atomic(), reversion.create_revision():
        self.object.save()
        #    reversion.set_user(self.request.user)

        messages.success(self.request, "You successfully send an invite to member! User got an invite and could accept it.")
        return HttpResponseRedirect( reverse( 'project:project_view_members', args = [project_id] ) ) #to member list!

# пользователь принял приглашение в участники проекта
@login_required
def member_accept(request, member_id):
    member = get_object_or_404( Member, pk = member_id )

    # проверить - а тот ли юзер?
    if ( member.member_profile.user == request.user ):
        member.set_member_accept()
        return HttpResponseRedirect( member.project.get_absolute_url() )
    else:
        # сбой - юзер не тот!!!
        return HttpResponseForbidden()

# админ проекта принял запрос пользователя на включение в проект
@login_required
def team_accept(request, member_id):
    member = get_object_or_404( Member, pk = member_id )
    project = member.project

    # проверить - админ ли
    if ( project.is_admin( request.user ) ):
        member.set_team_accept()
        member.set_change_user( request.user )
        member.save()
        return HttpResponseRedirect( project.get_absolute_url() )
    else:
        # сбой - юзер не тот!!!
        return HttpResponseForbidden()

@login_required
def member_remove_check(request, member_id):
    return member_remove(request, member_id, False )

@login_required
def member_remove_confirm(request, member_id):
    return member_remove(request, member_id, True )

def member_remove(request, member_id, arg_confirm_step ):
    member = get_object_or_404( Member, pk = member_id )
    member_user = member.member_profile.user
    project = member.project

    # проверить - админ ли
    if ( project.is_admin( request.user ) ):

        tasks = Get_User_Project_Tasks( member_user, project )

        can_remove = ( tasks.count() == 0 )

        if arg_confirm_step and can_remove:
            member.delete()
            messages.success(request, "You was removed the member from project!")
            if request.user == member_user: # you was delete yourselves and may loose the access to this project
                return HttpResponseRedirect( reverse( 'project:index' ) ) #to projects list!
            else:
                return HttpResponseRedirect( reverse( 'project:project_view_members', args = [project.pk] ) ) #to member list!
        else:
            context_dict = { 'project' : project,
                             'member' : member,
                             'tasks' : tasks,
                             'can_remove' : can_remove,
                           }
            return render( request, 'project/member_remove.html', context_dict )
    else:
        # сбой - юзер не тот!!!
        return HttpResponseForbidden()

# текущий пользователь хочет присоединится к участникам проекта
@login_required
def member_want_join(request, project_id):
    #определить текущего юзера
    curr_user = request.user
    if curr_user.is_authenticated:
        # определить проект
        if not ( project_id is None ):
            project = get_object_or_404( Project, pk = project_id )
            # проверить, есть ли у него доступ на просмотр

            m = Member( project = project )
            m.set_user_want_join( curr_user )
            messages.info(request, "You successfully send a join request to project admin! Admin got a request and could accept it.")
            return HttpResponseRedirect( project.get_absolute_url() )
        else:
            Http404
    else:
        return HttpResponseForbidden()
    #member = get_object_or_404( Member, pk = member_id )

    # проверить - а тот ли юзер?
    #if ( member.member_profile.user == request.user ):
    #    member.set_member_accept()
    #    return HttpResponseRedirect( member.project.get_absolute_url() )
    #else:
    #    # сбой - юзер не тот!!!
    #    return HttpResponseForbidden()

class TaskCreateView(LoginRequiredMixin, CreateView):

    form_class = TaskForm
    model = Task

    p = None
    m = None

    def get_initial(self):
        # если задана веха
        holder = self.request.user.profile
        try:
            milestone_id = self.kwargs['milestone_id']
            self.m = get_object_or_404( Milestone, pk = milestone_id )
            self.p = self.m.project
            return { 'project': self.p, 'holder' : holder, 'milestone' : self.m }
        except:
            milestone_id = None
            self.p = get_object_or_404( Project, pk = self.kwargs['project_id'])
            return { 'project': self.p, 'holder' : holder, }

    def form_valid(self, form):
        project_id = None
        milestone_id = None
        if 'project_id' in self.kwargs:
            project_id = self.kwargs['project_id']
        else:
            if 'milestone_id' in self.kwargs:
                milestone_id = self.kwargs['milestone_id']
            else:
                raise Http404()

        self.object = form.save(commit=False)
        self.object.set_change_user(self.request.user)
        if not ( project_id is None ):
            p = get_object_or_404( Project, pk = project_id )
            self.object.project = p
        else:
            if not ( milestone_id is None ):
                p = get_object_or_404( Milestone, pk = milestone_id ).project
                self.object.project = p

        with transaction.atomic(), reversion.create_revision():
            reversion.set_user(self.request.user)
            self.object.save()

        messages.success(self.request, "You successfully create the task!")
        return HttpResponseRedirect(self.get_success_url())

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    form_class = TaskForm
    model = Task

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.set_change_user(self.request.user)
        with transaction.atomic(), reversion.create_revision():
            reversion.set_user(self.request.user)
            self.object.save()

        return HttpResponseRedirect(self.get_success_url())

def task_history(request, task_id):
    context = RequestContext(request)
    task = get_object_or_404( Task, pk=task_id)
    ual = task.project.user_access_level( request.user )
    if ual == PROJECT_ACCESS_NONE:
        raise Http404()

    versions = Version.objects.get_for_object( task )

    context_dict = { 'task': task,
                     'versions': versions }

    # Рендерить ответ
    return render( request, 'project/task_history.html', context_dict )

def task_view(request, task_id):
    # Получить контекст запроса
    context = RequestContext(request)

    try:
        task = get_object_or_404( Task, pk=task_id)

        user_can_comment = False
        user_can_work = False
        user_can_admin = False

        user_comment_actions = { }

        ual = task.project.user_access_level( request.user )
        if ual == PROJECT_ACCESS_NONE:
            # если пользователь не авторизован, то доступ только к открытым проектам и только на просмотр
            if ( request.user is None ) or ( not request.user.is_authenticated ):
                return handle_redirect_to_login( request, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None )
            else:
                raise Http404()
        else:
            if ual == PROJECT_ACCESS_WORK:
                user_can_work = True
                user_can_comment = True
            else:
                if ual == PROJECT_ACCESS_ADMIN:
                    user_can_work = True
                    user_can_admin = True
                    user_can_comment = True
                else:
                    if ual == PROJECT_ACCESS_VIEW and task.get_opened() and request.user.is_authenticated:
                        user_can_comment = True

        # user has an access, so go close all unreaded notifications about this task
        if ( not request.user is None ) and ( request.user.is_authenticated ):
            task_type = ContentType.objects.get(app_label='project', model='task')
            Close_All_Unread_Notifications_For_Task_For_One_User( request.user, task_type, task.id )

        comments = task.get_comments()
        # user should see only available tasks - to prevent 404 if attempting to follow the link
        subtasks = TaskLink.objects.filter(maintask=task).filter( subtask__project__in = GetAvailableProjectList( request.user ) )
        maintasks = TaskLink.objects.filter(subtask=task)
        task_checklist = TaskCheckList.objects.filter( parenttask = task )
        task_properties = Task_Property_Amount.objects.filter( task = task )
        profiles = task.get_profiles().order_by('profile__profile_type')
        domains = Task2Domain.objects.filter(task=task)

        if task.state == TASK_STATE_NEW:
            user_comment_actions = TASK_OPEN_DETAIL_STATE_TITLES
        else:
            user_comment_actions = {}

        wanted_detailed_task_state = 0
        # доступ списку коментов открыт, а форму показывать не надо
        if request.user.is_authenticated:
            if request.method == "POST":
                if 'submit' in request.POST:
                    # добавить коментарий
                    wanted_task_state = TASK_STATE_NEW
                else:
                    if 'submit_and_close' in request.POST:
                        wanted_task_state = TASK_STATE_CLOSED
                    else:
                        if 'submit_and_reopen' in request.POST:
                            wanted_task_state = TASK_STATE_NEW
                        else:
                            # анализ подвидов состояний
                            some_state_found = False
                            for s in TASK_OPEN_DETAIL_STATE_TITLES:
                                if str( s ) in request.POST:
                                    some_state_found = True
                                    wanted_task_state = TASK_STATE_NEW
                                    wanted_detailed_task_state = s

                            if not some_state_found:
                                raise Exception("Inknown task state!")

                task_comment_form = TaskCommentForm(request.POST)

                if task_comment_form.is_valid():
                    c = task_comment_form.save(commit=False)
                    c.parenttask = task
                    if ( strip_tags( c.comment ) == '' ) and ( wanted_detailed_task_state > 0 ):
                        c.comment = TASK_OPEN_DETAIL_STATE_TITLES[ wanted_detailed_task_state ]

                    with transaction.atomic(), reversion.create_revision():
                        reversion.set_user(request.user)
                        c.set_change_user(request.user)
                        c.save()

                    if ( wanted_task_state != task.state ) or ( wanted_detailed_task_state > 0 ) :
                        task.set_task_state(request.user, wanted_task_state, wanted_detailed_task_state )
                    return HttpResponseRedirect( task.get_absolute_url() )
            else:
                task_comment_form = TaskCommentForm()
        else:
            task_comment_form = None

        # Записать список в словарь
        context_dict = { 'task': task,
                         'comments': comments,
                         'subtasks' : subtasks,
                         'profiles' : profiles,
                         'domains' : domains,
                         'maintasks' : maintasks,
                         'task_checklist' : task_checklist,
                         'task_properties' : task_properties,
                         'task_comment_form': task_comment_form,
                         'user_can_work' : user_can_work,
                         'user_can_admin' : user_can_admin,
                         'user_can_comment' : user_can_comment,
                         'user_comment_actions' : user_comment_actions,
                         }

    except Task.DoesNotExist:
        # На случай, если объекта нет - ничего не делаем, пусть об этом думает шаблон
        pass

    # Рендерить ответ
    return render( request,  'project/task.html', context_dict )

@login_required
def task_checklist(request, task_id):
    # Получить контекст запроса
    context = RequestContext(request)

    task = get_object_or_404( Task, pk=task_id)

    # взять контрольный список для задачи
    task_checklist = TaskCheckList.objects.filter( parenttask = task )

    # заказать у фабрики формсет

    TaskCheckListFormSet = modelformset_factory( TaskCheckList, form=TaskCheckListForm, extra = 3 )
    if request.method == 'POST':
        formset = TaskCheckListFormSet(request.POST, queryset=task_checklist )
        if formset.is_valid():
            # если верить https://docs.djangoproject.com/en/1.6/topics/forms/modelforms/#saving-objects-in-the-formset,
            # то в instances входят только измененные данные
            instances = formset.save(commit=False)

            for instance in instances:
                # кто автор изменений?
                instance.set_change_user(request.user)
                # указать для новых мастер-задачу
                instance.parenttask = task

                # история
                with transaction.atomic(), reversion.create_revision():
                    reversion.set_user(request.user)
                    instance.save()

            messages.success(request, "You successfully edit the check list!")
            return HttpResponseRedirect( task.get_absolute_url() )

    else:
        formset = TaskCheckListFormSet(queryset=task_checklist)

    context_dict = { 'task': task,
                     'task_checklist' : task_checklist,
                     'formset': formset,
                        }

    # Рендерить ответ
    return render( request, 'project/task_checklist.html', context_dict )

@login_required
def task_add_property(request, task_id):
    # Получить контекст запроса
    context = RequestContext(request)

    task = get_object_or_404( Task, pk=task_id)

    if request.method == 'POST':
        form = Task_Property_Amount_Form( request.POST, arg_allowed_properties = None )
        if form.is_valid():
            ta = form.save(commit=False)
            ta.task = task

            with transaction.atomic(), reversion.create_revision():
                reversion.set_user(request.user)
                ta.set_change_user(request.user)
                ta.save()

            # перебросить пользователя на задание
            messages.success(request, "You successfully add the property to task!")
            return HttpResponseRedirect('/project/task/' + task_id )
        else:
            print( form.errors )
    else:
        allowed_properties = Task_Property_Type.objects.exclude( task_property_amount__task_id = task_id )
        form = Task_Property_Amount_Form( arg_allowed_properties = allowed_properties )

    return render( request, 'project/task_add_property.html',
            {'task_id': task_id,
             'task' : task,
             'form': form,
             } )

@login_required
def task_edit_property(request, task_property_id):
    context = RequestContext(request)

    tpa = get_object_or_404( Task_Property_Amount, pk=task_property_id )
    task_id = tpa.task_id

    if request.method == 'POST':
        form = Task_Property_Amount_Form( request.POST, instance = tpa )
        if form.is_valid():
            tpa = form.save(commit=False)

            with transaction.atomic(), reversion.create_revision():
                reversion.set_user(request.user)
                tpa.set_change_user(request.user)
                tpa.save()

            # перебросить пользователя на задание
            messages.success(request, "You successfully edit the property amount for the task!")
            return HttpResponseRedirect('/project/task/' + str( task_id ) )
        else:
            print( form.errors )
    else:
        form = Task_Property_Amount_Form( instance = tpa )

    return render( request, 'project/task_add_property.html',
            { 'tpa' : tpa,
             'form': form,
             } )

@login_required
def edit_task_comment(request, task_comment_id):
    context = RequestContext(request)

    tc = get_object_or_404( TaskComment, pk=task_comment_id )

    if ( request.user != tc.created_user ):
        raise Http404()

    if request.method == 'POST':
        form = TaskCommentForm(request.POST, instance=tc)

        if form.is_valid():
            tc.set_change_user(request.user)
            with transaction.atomic(), reversion.create_revision():
                reversion.set_user(request.user)
                form.save()

            # перебросить пользователя на просмотр изделия
            messages.success(request, "You successfully updated this comment!")
            return HttpResponseRedirect( tc.parenttask.get_absolute_url() )
        else:
            print( form.errors )
    else:
        form = TaskCommentForm( instance=tc )

    return render( request, 'project/task_comment_edit_form.html',
            {'form': form, 'task_comment':tc} )

def task_comment_history(request, task_comment_id):
    context = RequestContext(request)
    tc = get_object_or_404( TaskComment, pk=task_comment_id )

    versions = Version.objects.get_for_object( tc )

    context_dict = { 'tc': tc,
                     'versions': versions }

    # Рендерить ответ
    return render( request, 'project/task_comment_history.html', context_dict )

@login_required
def add_linked(request, task_id):
    context = RequestContext(request)

    main_task = get_object_or_404( Task, pk=task_id )

    task_filter = TaskFilter_for_Linking( data = request.GET, request=request, queryset= Task.objects.filter(project__in=GetMemberedProjectList(request.user)).exclude(id=task_id).exclude( sub__maintask = task_id ) )

    if task_filter.Search_is_new():
        qs = Task.objects.filter( pk = 0 ) # do not use None - query set is required for FORM
        task_filter.data = { 'state' : TASK_STATE_NEW, 'project': main_task.project.id }
    else:
        qs = task_filter.qs

    if request.method == 'POST':
        form = TaskLinkedForm( request.POST, arg_qs = qs )
        if form.is_valid():
            for st in form.cleaned_data['subtasks']:
                tl = TaskLink()
                tl.maintask=main_task
                tl.subtask = st
                tl.save()
            # перебросить пользователя на задание
            return HttpResponseRedirect('/project/task/' + task_id )
        else:
            print( form.errors )
    else:
        form = TaskLinkedForm( arg_qs = qs )

    return render( request, 'project/task_add_link.html',
            {'task_id': task_id,
              'main_task' : main_task,
             'form': form,
             'task_filter' : task_filter,
             } )

@login_required
def task_unlink(request, tasklink_id):
    context = RequestContext(request)
    # если запись не будет найдена, то дальше будет редирект на 404
    maintask = None
    try:
        tasklink = TaskLink.objects.get( id = tasklink_id )
        maintask = tasklink.maintask
        ual = maintask.project.user_access_level( request.user )
        if ual in ( PROJECT_ACCESS_WORK, PROJECT_ACCESS_ADMIN ):
            tasklink.delete()
            messages.success(request, "You've unlink the subtask from task!")
            return HttpResponseRedirect( maintask.get_absolute_url() )
        else:
            raise Http404()
    except:
        raise Http404()

@login_required
def project_task_domain_unlink(request, taskdomain_id):
    context = RequestContext(request)

    # если запись не будет найдена, то дальше будет редирект на 404
    maintask = None
    try:
        taskdomain = Task2Domain.objects.get( id = taskdomain_id )
        maintask = taskdomain.task
        ual = maintask.project.user_access_level( request.user )
        if ual in ( PROJECT_ACCESS_WORK, PROJECT_ACCESS_ADMIN ):
            taskdomain.delete()
            messages.success(request, "You've unlink the domain from task!")
            return HttpResponseRedirect( maintask.get_absolute_url() )
        else:
            raise Http404()
    except:
        raise Http404()

# add_user - True for user, False for other kind of profiles
@login_required
def add_user_or_profile(request, task_id, add_user, arg_level_pk = 0 ):
    context = RequestContext(request)
    task = get_object_or_404( Task, pk = task_id )
    level_pk = int( arg_level_pk )
    root_profile = None
    level_profiles = None

    if add_user:
        # select only users
        query_for_combo = Get_Profiles_Available2Task( task_id ) # base query - all types profiles, unassigned
        query_for_combo = query_for_combo.filter( profile_type = PROFILE_TYPE_USER, user__is_active = True ) # only users and only active users
    else:
        # select profiles (except users) and build tree navigation
        if level_pk > 0:
            root_profile = get_object_or_404( Profile, pk = level_pk )
        else:
            root_profile = None
        level_profiles = Get_Profiles_From_Level( level_pk )
        query_for_combo = ( level_profiles.distinct() & Get_Profiles_Available2Task( task_id ) ).exclude( profile_type = PROFILE_TYPE_USER ) # unlinked, from current level and except users
        level_profiles = level_profiles.filter(  profile_type__in = PROFILE_TYPE_FOR_TREE )

    if request.method == 'POST':
        form = TaskProfileForm(request.POST, argmaintaskid = task_id, arg_query_for_combo = query_for_combo )

        if form.is_valid():
            tp = form.save(commit=False)
            tp.parenttask=task
            tp.set_change_user(request.user)
            tp.save()
            # перебросить пользователя на задание
            return HttpResponseRedirect('/project/task/' + task_id )
        else:
            print( form.errors )
    else:
        form = TaskProfileForm( argmaintaskid = task_id, arg_query_for_combo = query_for_combo )

    return render( request, 'project/task_add_profile.html',
            {'task_id': task_id,
             'task' : task,
             'form': form,
             'add_user' : add_user,
             'level_pk' : level_pk,
             'root_profile' : root_profile,
             'level_profiles' : level_profiles
             } )

@login_required
def switch_assign_responsibillty(request, taskprofile_id, priority_int ):
    tp = get_object_or_404( TaskProfile, pk = taskprofile_id )
    try:
        priority_int = int( priority_int )
        if tp.priority != priority_int:
            tp.priority = priority_int
            tp.set_change_user(request.user)
            tp.save()
    except:
        messages.error( request, "Can't set wrong priority!")

    # перебросить пользователя на задание
    return HttpResponseRedirect('/project/task/' + str( tp.parenttask_id ) )

@login_required
def remove_assign_responsibillty(request, taskprofile_id):
    tp = get_object_or_404( TaskProfile, pk = taskprofile_id )

    tp.delete()

    # перебросить пользователя на задание
    return HttpResponseRedirect('/project/task/' + str( tp.parenttask_id ) )

@login_required
def add_profile(request, task_id, level_pk = 0):
    return add_user_or_profile(request, task_id, False, level_pk)

@login_required
def add_user(request, task_id):
    return add_user_or_profile(request, task_id, True )

@login_required
def add_domain(request, task_id):
    context = RequestContext(request)

    if request.method == 'POST':
        form = TaskDomainForm(request.POST, argmaintaskid = task_id )

        if form.is_valid():
            tp = form.save(commit=False)
            tp.task=Task.objects.get(id=task_id)
            tp.set_change_user(request.user)
            tp.save()
            # перебросить пользователя на задание
            return HttpResponseRedirect('/project/task/' + task_id )
        else:
            print( form.errors )
    else:
        form = TaskDomainForm( argmaintaskid = task_id )

    return render( request, 'project/task_add_domain.html',
            {'task_id': task_id,
             'form': form} )

@login_required
def task_check_switch(request, task_check_id):
    #context = RequestContext(request)
    check = get_object_or_404( TaskCheckList, pk = task_check_id )

    with transaction.atomic(), reversion.create_revision():
        reversion.set_user(request.user)
        check.check_flag = not check.check_flag
        check.save()

    # перебросить пользователя на задание
    return HttpResponseRedirect('/project/task/%i' % check.parenttask_id )

@login_required
def view_my_schedule(request):
    profile_id = request.user.profile.id

    if profile_id > 0:
        return view_profile_schedule(request, profile_id)
    else:
        raise Http404()

@login_required
def view_profile_schedule(request, profile_id):
    profile = get_object_or_404( Profile, pk = profile_id )

    owner_page = ( profile.user == request.user )
    profile_is_managed = Is_User_Manager( request.user, profile )
    if ( not owner_page ) and ( not profile_is_managed ):
        raise Http404()

    schedules = Get_Profile_ScheduleItem( profile ).annotate(Count('scheduleitem_task')).order_by( '-schedule_date_start' )

    offer_to_create_this_week = False
    offer_to_create_next_week = False

    if ( request.user == profile.user ) or ( profile_is_managed ):
        offer_to_create_this_week = not Get_Profile_ScheduleItem_This_Week( schedules ).exists()
        offer_to_create_next_week = not Get_Profile_ScheduleItem_Next_Week( schedules ).exists()

    return render( request, 'project/schedule_index.html',
            { 'schedules' : schedules,
              'profile' : profile,
              'owner_page' : owner_page,
              'profile_is_managed' : profile_is_managed,
              'offer_to_create_this_week' : offer_to_create_this_week,
              'offer_to_create_next_week' : offer_to_create_next_week,

            } )

@login_required
def create_schedule_current(request, profile_id = 0 ):
    return create_schedule(request, False, int( profile_id ) )

@login_required
def create_schedule_next(request, profile_id = 0 ):
    return create_schedule(request, True, int( profile_id ) )

@login_required
def create_schedule(request, arg_next, arg_profile_id ):
    if arg_profile_id > 0:
        profile = get_object_or_404( Profile, pk = arg_profile_id )
    else:
        profile = request.user.profile

    schedule_item = Create_ScheduleItem( request.user, profile, arg_next )

    messages.success(request, "New schedule is created" )

    return HttpResponseRedirect( schedule_item.get_absolute_url() )

@login_required
def schedule_item_view(request, schedule_item_id ):
    schedule = get_object_or_404( ScheduleItem, pk=schedule_item_id )
    schedule_profile = schedule.schedule_profile

    # show page only for owner
    owner_page = ( schedule_profile.user == request.user )
    profile_is_managed = Is_User_Manager( request.user, schedule_profile )
    if ( not owner_page ) and ( not profile_is_managed ):
        raise Http404()

    my_task = Get_User_Tasks(schedule_profile.user)

    scheduled_task_items = ScheduleItem_Task.objects.filter( schedule_item = schedule )
    unscheduled_tasks = my_task.exclude( scheduledtask__in = scheduled_task_items )

    can_edit = owner_page or profile_is_managed

    return render( request, 'project/schedule_item.html',
            { 'schedule' : schedule,
              'scheduled_task_items' : scheduled_task_items,
              'unscheduled_tasks' : unscheduled_tasks,
              'schedule_profile' : schedule_profile,
              'owner_page' : owner_page,
              'profile_is_managed' : profile_is_managed,
              'can_edit' : can_edit,
            } )

@login_required
def schedule_one_task( request, schedule_item_id, task_id ):

    schedule = get_object_or_404( ScheduleItem, pk=schedule_item_id )
    task = get_object_or_404( Task, pk=task_id )

    added_task = ScheduleItem_Task( schedule_item = schedule, scheduledtask = task )
    added_task.set_change_user(request.user)
    added_task.save()

    messages.success(request, "Task '" + str(task) + "' was added to schedule!" )

    return HttpResponseRedirect( reverse( 'project:schedule_item_view', args = [schedule_item_id]  ) )

@login_required
def unschedule_one_task( request, schedule_item_id, task_id ):
    schedule = get_object_or_404( ScheduleItem, pk=schedule_item_id )
    schedule_task = get_object_or_404( ScheduleItem_Task, schedule_item = schedule_item_id, scheduledtask = task_id )

    task_name = str( schedule_task.scheduledtask )
    schedule_task.delete()

    messages.success(request, "Task " + task_name  +  " was excluded from schedule!" )
    return HttpResponseRedirect( reverse( 'project:schedule_item_view', args = [schedule_item_id]  ) )

@login_required
def task_move2project( request, task_id, project_id = 0 ):

    task = get_object_or_404( Task, pk=task_id )
    target_project_id = int( project_id )

    if not task.can_be_moved():
        error_mesage = "Can't move this task, because it was linked to sub project!!"
        return render( request, 'project/task_move2project.html',
            { 'task' : task,
              'error_mesage'   : error_mesage,
            } )

    if target_project_id > 0:
        can_move_task = False
        error_mesage = ""
        target_project = get_object_or_404( Project, pk=target_project_id )

        # checks
        if target_project_id == task.project.id:
            error_mesage = "Can't move the task to the same project"
        else:
            task_interested = GetTask_Interested( task )
            for ti in task_interested:
                if not target_project.is_member( ti ):
                    if can_move_task:
                        can_move_task = False

                    error_mesage = error_mesage + 'Task user ' + str( ti ) + ' is not a member of ' + str( target_project ) + '    </br>'

            can_move_task = error_mesage == ""

        if can_move_task:
            with transaction.atomic(), reversion.create_revision():
                reversion.set_user(request.user)
                task.project_id = target_project_id
                task.set_change_user(request.user)
                task.save()

            messages.success(request, "You have moved task " + str( task )  +  " to another project." )
            return HttpResponseRedirect( reverse( 'project:task_view', args = [task_id] ) )
        else:
            return render( request, 'project/task_move2project.html',
                { 'task' : task,
                  'error_mesage'   : error_mesage,
                } )
    else:
        available_projects = GetAvailableProjectList(request.user).exclude( id = task.project.id )

        return render( request, 'project/task_move2project.html',
                { 'task' : task,
                  'available_projects' : available_projects,
                } )

class Sub_ProjectCreateView(LoginRequiredMixin, CreateView):
    form_class = Sub_ProjectForm
    model = Sub_Project

    def form_valid(self, form):
        if 'project_id' in self.kwargs:
            project_id = self.kwargs['project_id']
        else:
            raise Http404()

        self.object = form.save(commit=False)
        self.object.set_change_user(self.request.user)
        if not ( project_id is None ):
            p = get_object_or_404( Project, pk = project_id )
            self.object.project = p

        with transaction.atomic(), reversion.create_revision():
            reversion.set_user(self.request.user)
            self.object.save()

        messages.success(self.request, "You successfully create the subproject!")
        return HttpResponseRedirect(self.get_success_url())

class Sub_ProjectUpdateView(LoginRequiredMixin, UpdateView):
    form_class = Sub_ProjectForm
    model = Sub_Project

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.set_change_user(self.request.user)
        with transaction.atomic(), reversion.create_revision():
            reversion.set_user(self.request.user)
            self.object.save()

        messages.success(self.request, "You successfully update the sub project!")
        return HttpResponseRedirect(self.get_success_url())

def sub_project_history(request, sub_project_id):
    context = RequestContext(request)

    sub_project = get_object_or_404( Sub_Project, pk=sub_project_id)

    versions = Version.objects.get_for_object( sub_project )

    context_dict = { 'sub_project': sub_project,
                     'versions': versions }

    return render( request, 'project/sub_project_history.html', context_dict )

def sub_project_view(request, sub_project_id):
    context = RequestContext(request)

    sub_project = get_object_or_404( Sub_Project, pk=sub_project_id)

    ual = sub_project.project.user_access_level( request.user )
    user_can_work = False
    user_can_admin = False
    if ual == PROJECT_ACCESS_NONE:
        raise Http404()
    else:
        if ual == PROJECT_ACCESS_WORK:
            user_can_work = True
        else:
            if ual == PROJECT_ACCESS_ADMIN:
                user_can_work = True
                user_can_admin = True

    tasks = Task.objects.filter( sub_project = sub_project ).order_by('state')

    context_dict = { 'sub_project': sub_project,
                     'tasks' : tasks,
                     'user_can_admin' : user_can_admin,
                     'user_can_work' : user_can_work,
                         }

    return render( request, 'project/sub_project.html', context_dict )
