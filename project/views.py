from project.models import *
from project.forms import ProjectForm, TaskForm, TaskCommentForm, MilestoneForm, MemberForm, TaskLinkedForm, TaskEditTargetDateForm, TaskCheckListForm, ResourceForm

from django.forms.models import modelformset_factory

from django.utils import timezone

# Create your views here.

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib import messages

from django.template import RequestContext

#from django.contrib.auth.decorators import login_required
from account.decorators import login_required

from django.db import transaction
import reversion
from reversion.models import Version

from project.filters import ProjectFilter, TaskFilter

# константы фильров по проектам
PROJECT_FILTER_MINE = 0
PROJECT_FILTER_SEARCH_PUBLIC = 1
PROJECT_FILTER_ALL_PUBLIC = 2

def get_index( request, arg_page = PROJECT_FILTER_MINE ):
    # Получить контекст из HTTP запроса.
    context = RequestContext(request)
    if arg_page == PROJECT_FILTER_MINE:
        my_task = None
        if request.user.is_authenticated():
            my_task = Task.objects.filter( state = TASK_STATE_NEW, assigned_user = request.user )
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
                raise Http404()

    # Сформировать ответ, отправить пользователю
    return render( request, 'project/index.html', context_dict, context)
    
def index( request ):
    return get_index( request )
    
def index_search_public( request ):
    return get_index( request, PROJECT_FILTER_SEARCH_PUBLIC )
    
def index_public( request ):
    return get_index( request, PROJECT_FILTER_ALL_PUBLIC )
    
from account.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView
    
class ProjectCreateView(LoginRequiredMixin, CreateView):

    form_class = ProjectForm
    model = Project
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
TASK_FILTER_SEARCH = 2

def project_view(request, project_id):
    return get_project_view(request, project_id )

def project_view_closed_tasks(request, project_id):
    return get_project_view(request, project_id, TASK_FILTER_CLOSED)
    
def project_view_search_tasks(request, project_id):
    return get_project_view(request, project_id, TASK_FILTER_SEARCH )

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
    
def get_project_view(request, project_id, arg_task_filter = TASK_FILTER_OPEN ):
    # Получить контекст запроса
    context = RequestContext(request)
    project = get_object_or_404( Project, pk=project_id)
    
    user_can_work = False
    user_can_admin = False
    
    ual = project.user_access_level( request.user )
    if ual == PROJECT_ACCESS_NONE:
        raise Http404()
    else:
        if ual == PROJECT_ACCESS_WORK:
            user_can_work = True
        else:
            if ual == PROJECT_ACCESS_ADMIN:
                user_can_work = True
                user_can_admin = True

    members = project.GetMemberList()
    milestones = Milestone.objects.filter(project = project).order_by('finished_at')
    
    filter_type = ''
    filter = None
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
                # тут хитрость. tasks в других случаях это готовый датасет. а здесь - это фильтр, способный генерировать как форму с параметрами так и датасет
                tasks = TaskFilter( request.GET, queryset=base_tasks )                
                tasks.filters['milestone'].extra['queryset'] = milestones
            else:
                raise Http404    
 
    # Записать список в словарь
    context_dict = { 'project': project, 
                     'members':members,
                     'milestones' : milestones,
                     'tasks' : tasks,
                     'filter': tasks,
                     'filter_type' : filter_type,
                     'user_can_work' : user_can_work,
                     'user_can_admin' : user_can_admin,
                         }

    # Рендерить ответ
    return render( request, 'project/project.html', context_dict )
    
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
    user_can_admin = milestone.project.can_admin( request.user )

    tasks = Task.objects.filter( milestone = milestone ).order_by('state')
        
    # Записать список в словарь
    context_dict = { 'milestone': milestone,
                     'tasks' : tasks,
                     'user_can_admin' : user_can_admin,
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
        return HttpResponseRedirect(self.object.project.get_absolute_url() )

# пользователь принял приглашение в участники проекта
def member_accept(request, member_id):
    member = get_object_or_404( Member, pk = member_id )
    
    # проверить - а тот ли юзер?
    if ( member.member_user == request.user ):
        member.set_member_accept()
        member.save()
        return HttpResponseRedirect( member.project.get_absolute_url() )
    else:
        # сбой - юзер не тот!!!
        return HttpResponseForbidden()
        
class TaskCreateView(LoginRequiredMixin, CreateView):

    form_class = TaskForm
    model = Task
    
    p = None
    m = None
    
    def get_initial(self):        
        # если задана веха
        holder = self.request.user
        try:
            milestone_id = self.kwargs['milestone_id']
            self.m = get_object_or_404( Milestone, pk = milestone_id )
            self.p = self.m.project
            return { 'project': self.p, 'holder_user' : holder, 'milestone' : self.m }
        except:
            milestone_id = None
            self.p = get_object_or_404( Project, pk = self.kwargs['project_id'])
            return { 'project': self.p, 'holder_user' : holder, }
        
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
        
        ual = task.project.user_access_level( request.user )
        if ual == PROJECT_ACCESS_NONE:
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
                    if ual == PROJECT_ACCESS_VIEW and task.get_opened() and request.user.is_authenticated():
                        user_can_comment = True
        
        comments = TaskComment.objects.filter( parenttask = task )
        subtasks = TaskLink.objects.filter(maintask=task)
        maintasks = TaskLink.objects.filter(subtask=task)
        task_checklist = TaskCheckList.objects.filter( parenttask = task )
        
        # доступ списку коментов открыт, а форму показывать не надо
        if request.user.is_authenticated():
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
                            raise Exception("Inknown task state!")
                        
                    
                task_comment_form = TaskCommentForm(request.POST)
                
                if task_comment_form.is_valid():
                    c = task_comment_form.save(commit=False)
                    c.parenttask = task
                    
                    with transaction.atomic(), reversion.create_revision():
                        reversion.set_user(request.user)
                        c.set_change_user(request.user)
                        c.save()
                    
                    if wanted_task_state != task.state :
                        task.set_task_state(request.user, wanted_task_state )
                    return HttpResponseRedirect( task.get_absolute_url() )
            else:
                task_comment_form = TaskCommentForm()
        else:
            task_comment_form = None
            
        # Записать список в словарь
        context_dict = { 'task': task,
                         'comments': comments,
                         'subtasks' : subtasks,
                         'maintasks' : maintasks,
                         'task_checklist' : task_checklist,
                         'task_comment_form': task_comment_form,
                         'user_can_work' : user_can_work,
                         'user_can_admin' : user_can_admin,
                         'user_can_comment' : user_can_comment,
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
def edit_task_target_date(request, pk):
    context = RequestContext(request)
    task = get_object_or_404( Task, pk=pk )
    if request.method == 'POST':        
        form = TaskEditTargetDateForm(request.POST, instance=task)
        
        if form.is_valid():
            task.set_change_user(request.user)
            with transaction.atomic(), reversion.create_revision():                
                reversion.set_user(request.user)
                form.save()            

            # перебросить пользователя на просмотр изделия
            messages.success(request, "You successfully updated this task target date!")
            return HttpResponseRedirect( task.get_absolute_url() )
        else:
            print( form.errors )
    else:        
        form = TaskEditTargetDateForm( instance=task )

    return render( request, 'project/task_edit_targed_date_form.html',
            {'form': form, 'task':task} )
    
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

    if request.method == 'POST':
        form = TaskLinkedForm(request.POST, argmaintaskid = task_id )

        if form.is_valid():
            tl = form.save(commit=False)
            tl.maintask=Task.objects.get(id=task_id)
            tl.save()
            # перебросить пользователя на задание
            return HttpResponseRedirect('/project/task/' + task_id )
        else:
            print( form.errors )
    else:
        form = TaskLinkedForm( argmaintaskid = task_id )

    return render( request, 'project/add_link.html',
            {'task_id': task_id,
             'form': form} )
             
@login_required
def task_unlink(request, tasklink_id):
    context = RequestContext(request)
    # если запись не будет найдена, то дальше будет редирект на 404
    maintask = None
    try:
        tasklink = TaskLink.objects.get( id = tasklink_id )
        maintask = tasklink.maintask
        tasklink.delete()
        return HttpResponseRedirect( maintask.get_absolute_url() )
    except:
        raise Http404()
             
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
    
def resource_list( request ):
    # Получить контекст из HTTP запроса.
    context = RequestContext(request)

    context_dict = { 'resource_list' : Resource.objects.all() }

    # Сформировать ответ, отправить пользователю
    return render_to_response('project/resource_list.html', context_dict, context)
    
def resource_view(request, resource_id ):
    # Получить контекст запроса
    context = RequestContext(request)
    resource = get_object_or_404( Resource, pk=resource_id )   

    tasks = resource.Get_Tasks( True )
    subresources = Resource.objects.filter(parent=resource)
    
    # Записать список в словарь
    context_dict = { 'resource': resource, 'subresources' : subresources, 'tasks' : tasks }

    # Рендерить ответ
    return render_to_response('project/resource.html', context_dict, context)
    
class ResourceCreateView(LoginRequiredMixin, CreateView):

    form_class = ResourceForm
    model = Resource
    
    def get_initial(self):
        try:
            parent_resource_id = self.kwargs['parent_resource_id']
        except:
            parent_resource_id = None
        
        if not parent_resource_id is None:
            parent = Resource.objects.get(id=parent_resource_id)
            return { 'parent':parent, }
        else:
            return { }

from mptt.exceptions import InvalidMove 
@login_required
def resource_edit(request, resource_id):
    context = RequestContext(request)
    
    resource = get_object_or_404( Resource, pk=resource_id )
    
    if request.method == 'POST':        
        form = ResourceForm(request.POST, instance=resource)
        
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "You successfully updated this resource!")
                return HttpResponseRedirect( resource.get_absolute_url() )
            except InvalidMove as e: 
                messages.warning(request, "Can't move resource here! Change parent!")
        else:
            print( form.errors )
    else:        
        form = ResourceForm( instance=resource )

    return render_to_response( 'project/resource_form.html',
            {'form': form, 'resource':resource},
             context)    
