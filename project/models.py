from django.db import models

from commons.models import BaseStampedModel
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from django.db import transaction
import reversion

import uuid

from ich_bau.profiles.notification_helper import Send_Notification
from ich_bau.profiles.models import Profile, GetProfileByUser

import markdown

def make_uuid():
    return uuid.uuid4() # https://docs.python.org/2/library/uuid.html

# access level
PROJECT_ACCESS_NONE  = 0 # нет доступа
PROJECT_ACCESS_VIEW  = 1 # просмотр
PROJECT_ACCESS_WORK  = 2 # может что-то делать: создавать и редактировать задачи, комментировать, закрывать и открывать задачи
PROJECT_ACCESS_ADMIN = 3 # админить проект - создавать и редактировать вехи, добавлять-удалять участников
# правила следующие
# для открытых проектов:
# - любой аноним может смотреть
# - любой авторизованный юзер может смотреть и работать. 
# - Админить может только их админ. Тогда в чем смысл участника? Что на него можно назначать задачи!
# для закрытых проектов:
# - аноним и авторизованный не участник их не видит
# - авторизованный участник может работать
# - админ может админить
    
@reversion.register()
class Project(BaseStampedModel):
    # shortname = models.CharField(max_length=255)
    # slug = models.SlugField( unique = True, default=make_uuid ) # заготовка параноикам
    fullname = models.CharField(max_length=255, verbose_name = 'Full name!')
    active_flag=models.BooleanField(blank=True, default=True)
    private_flag=models.BooleanField(blank=True, default=False, verbose_name = 'Private project')
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['fullname']
        
    # полный список членов проекта, независимо от статуса подтверждения
    def GetMemberList( self ):
        return Member.objects.filter( project = self )
    
    # список членов проекта     
    def GetFullMemberList( self ):
        q = Member.objects.filter( project = self, team_accept__isnull = False, member_accept__isnull = False )
        return q
        
    def GetFullMemberUsers( self ):
        q = Profile.objects.filter( member_profile__project = self, member_profile__team_accept__isnull = False, member_profile__member_accept__isnull = False )
        return q        
    
    def is_member( self, arg_user ):
        if ( arg_user is None ) or ( not arg_user.is_authenticated() ):
            return False # аноним никогда не участник
        else:
            return self.GetFullMemberUsers().filter( user = arg_user ).exists()
            
    def is_admin( self, arg_user ):
        if ( arg_user is None ) or ( not arg_user.is_authenticated() ):
            return False # аноним никогда не админ
        else:
            return self.GetFullMemberList().filter( member_profile__user = arg_user, admin_flag = True ).exists()
    
    def can_admin( self, arg_user ):
        # админить могут только админы, и для открытых, и для закрытых проектов
        # создавать и редактировать вехи
        return self.is_admin( arg_user )

    def can_view( self, arg_user ):
        # если проект открытый, то смотреть могут все
        # если закрытый, то только члены
        if self.private_flag:
            return self.is_member( arg_user )
        else:
            return True
    
    def user_access_level( self, arg_user ):
        member_level = None
        # если пользователь не авторизован, то доступ только к открытым проектам и только на просмотр
        if ( arg_user is None ) or ( not arg_user.is_authenticated() ):
            if self.private_flag:
                return PROJECT_ACCESS_NONE
            else:
                return PROJECT_ACCESS_VIEW            
        else:
            # предполагается 1 или ни единого. 
            try:
                m = self.GetMemberList().get( member_profile__user = arg_user )
                if ( not m ) or ( m is None ):
                    member_level = None
                else:
                    if not ( m.team_accept is None ) and not( m.member_accept is None ):
                        if m.admin_flag:
                            return PROJECT_ACCESS_ADMIN
                        else:
                            return PROJECT_ACCESS_WORK
                    else:
                        return PROJECT_ACCESS_VIEW
            except:
                member_level = None
                
        if member_level is None:
            if self.private_flag:
                return PROJECT_ACCESS_NONE
            else:
                return PROJECT_ACCESS_VIEW
    
    # список задач проекта. 
    #   arg_opened = None значит все
    #   arg_opened = True значит открытые
    #   arg_opened = False значит закрытые    
    def Get_Tasks( self, arg_opened = None ):
        q = Task.objects.filter( project = self )
        if arg_opened is None:
            return q
        else:
            return q.filter(finished_fact_at__isnull = arg_opened )
    
    def __str__(self):
        return self.fullname

    def get_absolute_url(self):
        return "/project/project/%i/" % self.id
        
    def description_html(self):
        return markdown.markdown(self.description)

class Member(BaseStampedModel):
    project = models.ForeignKey(Project, blank=False, null=False )
    member_profile = models.ForeignKey( Profile, blank=False, null=False, related_name = "member_profile" )
    admin_flag=models.BooleanField(blank=True, default=False, verbose_name = 'Admin')
    # флаг подтверждения со стороны админа проекта
    team_accept = models.DateTimeField( blank=True, null=True )
    # флаг подтверждения со стороны участника
    member_accept = models.DateTimeField( blank=True, null=True )
    
    class Meta:
        unique_together = ("project", "member_profile")
            
    def save(self, *args, **kwargs):
        super(Member, self).save(*args, **kwargs)
        # послать уведомление. самому себе посылать не надо. 
        if ( self.member_profile.user != self.modified_user ) and ( self.member_accept is None ):
            message_str = 'You are asked to accept the membership of ' + self.project.fullname + ' project team!'
            Send_Notification( self.modified_user, self.member_profile.user, message_str, self.project.get_absolute_url() )        
    
    def set_team_accept( self ):
        self.team_accept = timezone.now()
        
    def set_member_accept( self ):
        self.member_accept = timezone.now()
        
    @classmethod
    def make_admin_after_project_create(cls, sender, instance, created, **kwargs):
        if created:
            project_created = instance
            pm = cls( member_profile = GetProfileByUser( project_created.created_user), project=project_created, admin_flag = True, created_user = project_created.created_user, modified_user = project_created.created_user )
            pm.set_team_accept()
            pm.set_member_accept()            
            pm.save()
            
# http://stackoverflow.com/questions/25929165/create-model-after-group-has-been-created-django
post_save.connect(Member.make_admin_after_project_create, sender=Project)

@receiver(post_save, sender=Project)
def project_post_save_Notifier_Composer(sender, instance, **kwargs):
    # проект изменился - разослать уведомление всем участникам проекта - кроме автора изменений
    members = instance.GetFullMemberList().exclude( member_profile__user = instance.modified_user )
    message_str = 'Changes in the ' + instance.fullname + ' project'
    for m in members:
        Send_Notification( instance.modified_user, m.member_profile.user, message_str, instance.get_absolute_url() )
       
def GetAllPublicProjectList( ):
    return Project.objects.filter( private_flag = False )
    
def GetMemberedProjectList( arg_user ):
    # если он не авторизован, то и членства ни в одном проекте нет
    if ( arg_user is None ) or ( not arg_user.is_authenticated() ):
        return { }
    else:
        return Project.objects.filter( member__member_profile__user = arg_user ).order_by('-active_flag')
        
@reversion.register()
class Milestone(BaseStampedModel):
    project = models.ForeignKey(Project, blank=False, null=False )
    fullname = models.CharField(max_length=255, verbose_name = 'Full name!', blank=False, null=False )
    planned_at = models.DateTimeField( blank=True, null=True )
    finished_at = models.DateTimeField( blank=True, null=True )
    
    def __str__(self):
        return self.fullname
    
    def get_absolute_url(self):
        return "/project/milestone/%i/" % self.id
        
@receiver(post_save, sender=Milestone)
def milestone_post_save_Notifier_Composer(sender, instance, **kwargs):
    # веха изменилась - разослать уведомление всем участникам проекта - кроме автора изменений
    member_users = instance.project.GetFullMemberUsers().exclude( user = instance.modified_user )
    message_str = 'Changes in the milestone ' + instance.fullname + ' of ' + instance.project.fullname + ' project'
    for m in member_users:
        Send_Notification( instance.modified_user, m.user, message_str, instance.get_absolute_url() )     
        
# состояния задач

# 0 - new
# 1 - closed
TASK_STATE_NEW = 0
TASK_STATE_CLOSED = 1

TASK_STATE_LIST = ( TASK_STATE_NEW, TASK_STATE_CLOSED )

TASK_STATE_LIST_CHOICES = (
    ( TASK_STATE_NEW, 'New' ),
    ( TASK_STATE_CLOSED, 'Closed' ),
    )
            
@reversion.register()
class Task(BaseStampedModel):
    project = models.ForeignKey(Project, blank=False, null=False )
    fullname = models.CharField(max_length=255, verbose_name = 'Full name!' )
    description = models.TextField(blank=True, null=True)
    # была мысль, что applicant - это тикет в Servicedesk от определенного клиента. Но если тикеты в SD будут отдельно, то достаточно и holder
    # applicant = models.ForeignKey( Profile, blank=True, null=True, related_name = "Applicant" )
    assignee = models.ForeignKey( Profile, blank=True, null=True, related_name = "Assignee" )
    holder = models.ForeignKey(Profile, blank=True, null=True, related_name = "Holder" )
    
    state = models.PositiveSmallIntegerField( blank=False, null=False, default = TASK_STATE_NEW )
    # 0 - новая задача
    milestone = models.ForeignKey(Milestone, blank=True, null=True )
    target_date_at = models.DateTimeField( blank=True, null=True )
    finished_fact_at = models.DateTimeField( blank=True, null=True )
    important = models.BooleanField(blank=True, default=False)
    
    class Meta:
        ordering = ['-important', 'target_date_at']
        
    def set_task_state(self, argUser, argWantedState):
        if ( argWantedState != self.state ):
            if argWantedState in TASK_STATE_LIST:
                with transaction.atomic(), reversion.create_revision():
                    reversion.set_user(argUser)
                
                    self.set_change_user(argUser)
                    self.state = argWantedState
                    if ( argWantedState == TASK_STATE_NEW ) and ( not ( self.finished_fact_at is None ) ):
                        self.finished_fact_at = None
                    else:
                        if ( argWantedState == TASK_STATE_CLOSED ) and ( self.finished_fact_at is None ):
                            self.finished_fact_at = timezone.now()
                    self.save()
            else:
                raise Exception("Wrong task state!")
    
    # состояний, в которых задача закрыта, можно выдумать много
    def get_opened(self):
        return self.finished_fact_at is None
    
    def get_state_name(self):
        return TASK_STATE_LIST_CHOICES[ self.state ][1]
    
    def __str__(self):
        return self.fullname

    # проверки перед сохранением
    def save(self, *args, **kwargs):
        # проверить - есть ли данная веха у проекта?
        if ( self.milestone is None ) or ( self.milestone.project == self.project ):
            # проверить - назначение на участника?
            if ( self.assignee is None ) or ( self.assignee.user is None ) or ( self.project.is_member( self.assignee.user ) ):
                # проверить состояние
                if not ( self.state in TASK_STATE_LIST ):
                    raise Exception("Wrong task state!")
                else:
                    super(Task, self).save(*args, **kwargs) # Call the "real" save() method.
            else:
                raise Exception("Assignee is not a member!")
        else:
            raise Exception("Wrong milestone!")
    
    def get_absolute_url(self):
        return "/project/task/%i/" % self.id
        
    def description_html(self):
        return markdown.markdown(self.description)

# связи между задачами
class TaskLink(models.Model):
    maintask=models.ForeignKey( Task, related_name = 'main' )
    subtask=models.ForeignKey( Task, related_name = 'sub' )
    class Meta:
        unique_together = ("maintask", "subtask")
    
    def get_absolute_url(self):
        return "/project/task_link/%i/" % self.id
        
@reversion.register()
class TaskComment(BaseStampedModel):
    parenttask = models.ForeignKey( Task, null = False )
    comment = models.TextField(blank=False, null=False)
    
    def get_absolute_url(self):
        return "/project/task_comment/%i/" % self.id
        
    def __str__(self):
        # у коментария есть только длинный текст, поэтому выводить можно только реквизиты
        return str( self.created_user ) + " " + self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        
    def comment_html(self):
        return markdown.markdown(self.comment)

@reversion.register()
class TaskCheckList(BaseStampedModel):
    parenttask = models.ForeignKey( Task, null = False, related_name = 'parenttask'  )
    checkname = models.CharField( max_length=255, blank=False, null=False )
    check_flag=models.BooleanField(blank=True, default=False)
    convertedtask = models.ForeignKey( Task, default = None, null = True, related_name = 'convertedtask' )
    
    def get_absolute_url(self):
        return "/project/task_check/%i/" % self.id    
        
    def __str__(self):        
        return self.checkname

def GetTaskUsers( arg_task, arg_exclude_user ):
    return User.objects.filter( id = TaskComment.objects.values_list('created_user', flat = True).filter(parenttask = arg_task ).exclude( created_user = arg_exclude_user ).distinct() )
       
def Send_Notifications_For_Task( arg_sender_user, arg_msg, arg_list, arg_url, arg_task_assignee ):
    for m in arg_list:
        Send_Notification( arg_sender_user, m, arg_msg, arg_url )
    
    if not ( arg_task_assignee is None ) and ( arg_task_assignee != arg_sender_user ) and not ( arg_task_assignee in arg_list ):        
        Send_Notification( arg_sender_user, arg_task_assignee, arg_msg, arg_url )

@receiver(post_save, sender=Task)
def task_post_save_Notifier_Composer(sender, instance, **kwargs):
    # задание изменилось - разослать уведомление всем участникам задания - кроме автора изменений    
    
    task_users = GetTaskUsers( instance, instance.modified_user )
    
    message_str = 'Changes in the task ' + instance.fullname + ' of ' + instance.project.fullname + ' project'
    
    assignee_user = None
    if ( not ( instance.assignee is None ) ) and ( not ( instance.assignee.user is None ) ):
        assignee_user = instance.assignee.user
    Send_Notifications_For_Task( instance.modified_user, message_str, task_users, instance.get_absolute_url(), assignee_user )

@receiver(post_save, sender=TaskComment)
def taskcomment_post_save_Notifier_Composer(sender, instance, **kwargs):
    # Добавился (изменился) коментарий к задаче - разослать уведомление всем участникам задания - кроме автора изменений        
    
    if kwargs['created'] :
        s = 'New'
    else:
        s = 'Changed'
    task_users = GetTaskUsers( instance.parenttask, instance.modified_user )
    
    message_str = s + ' comment in the task ' + instance.parenttask.fullname + ' of ' + instance.parenttask.project.fullname + ' project'
    
    parenttask_assignee_user = None
    if ( not ( instance.parenttask.assignee is None ) ) and ( not ( instance.parenttask.assignee.user is None ) ):
        parenttask_assignee_user = instance.parenttask.assignee.user
    
    Send_Notifications_For_Task( instance.modified_user, message_str, task_users, instance.parenttask.get_absolute_url(), parenttask_assignee_user )