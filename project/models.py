﻿from django.db import models

from commons.models import BaseStampedModel
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from django.db import transaction
import reversion

from ich_bau.profiles.notification_helper import Send_Notification
from ich_bau.profiles.models import Profile, PROFILE_TYPE_USER, PROFILE_TYPE_FOR_TASK
from ich_bau.profiles.messages import *

from project.repo_wrapper import *

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
    fullname = models.CharField(max_length=255, verbose_name = 'Full name!')
    active_flag=models.BooleanField(blank=True, default=True)
    private_flag=models.BooleanField(blank=True, default=False, verbose_name = 'Private project')
    description = models.TextField(blank=True, null=True)
    repo_name = models.CharField( max_length=255, blank=True, null = True )

    class Meta:
        ordering = ['fullname']

    # полный список членов проекта, независимо от статуса подтверждения. Возвращает объекты Member
    def GetMemberList( self ):
        return Member.objects.filter( project = self )

    # список полных (полностью подтвержденных) членов проекта. Возвращает объекты Member
    def GetFullMemberList( self ):
        q = Member.objects.filter( project = self, team_accept__isnull = False, member_accept__isnull = False )
        return q

    # список полных (полностью подтвержденных) админов проекта. Возвращает объекты Member
    def GetFullMemberAdminList( self ):
        q = self.GetFullMemberList().filter( admin_flag = True )
        return q

    # список профилей полных (полностью подтвержденных) членов проекта. Возвращает объекты Profile
    def GetFullMemberProfiles( self ):
        q = Profile.objects.filter( member_profile__project = self, member_profile__team_accept__isnull = False, member_profile__member_accept__isnull = False )
        return q

    # список юзеров полных (полностью подтвержденных) членов проекта. Возвращает объекты User
    def GetFullMemberUsers( self ):
        q = User.objects.filter( profile__in=self.GetFullMemberProfiles() )
        return q

    def is_member( self, arg_user ):
        if ( arg_user is None ) or ( not arg_user.is_authenticated ):
            return False # аноним никогда не участник
        else:
            return self.GetFullMemberProfiles().filter( user = arg_user ).exists()

    def is_admin( self, arg_user ):
        if ( arg_user is None ) or ( not arg_user.is_authenticated ):
            return False # аноним никогда не админ
        else:
            return self.GetFullMemberAdminList().filter( member_profile__user = arg_user ).exists()

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

    # может ли юзер подать заявку на включение
    def can_join( self, arg_user ):
        return ( not self.private_flag ) and ( arg_user.is_authenticated ) and ( not self.GetMemberList().filter( member_profile__user = arg_user ).exists() )

    def user_access_level( self, arg_user ):
        member_level = None
        # если пользователь не авторизован, то доступ только к открытым проектам и только на просмотр
        if ( arg_user is None ) or ( not arg_user.is_authenticated ):
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
        return self.description

    def have_repo( self ): # True - да, repo есть
        s = self.repo_name
        return ( not ( s is None ) ) and ( s != '' )

    def add_repo_access( self ):
        # дать доступ к repo
        if self.have_repo():
            # дать доступ по всему списку членов проекта
            user_dict = { settings.REPO_SVN.get('SVN_ADMIN_USER') : settings.REPO_SVN.get('SVN_ADMIN_PASSWORD') }

            member_profiles = self.GetFullMemberProfiles()

            for mp in member_profiles:
                user_dict[ mp.user.username ] = mp.repo_pw

            Add_User_to_Repo( self.repo_name, user_dict )

class Member(BaseStampedModel):
    project = models.ForeignKey(Project, on_delete=models.PROTECT, blank=False, null=False )
    member_profile = models.ForeignKey( Profile, on_delete=models.PROTECT, blank=False, null=False, related_name = "member_profile" )
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
            message_str = project_msg2json_str( MSG_NOTIFY_TYPE_ASK_ACCEPT_ID, arg_project_name = self.project.fullname )
            Send_Notification( self.modified_user, self.member_profile.user, message_str, self.project.get_absolute_url() )

    def set_user_want_join( self, arg_user ):
        self.member_profile = arg_user.profile
        self.member_accept = timezone.now()
        self.set_change_user(arg_user)
        self.save()
        message_str = project_msg2json_str( MSG_NOTIFY_TYPE_USER_WANT_JOIN_ID, arg_project_name = self.project.fullname )
        for a in self.project.GetFullMemberAdminList():
            Send_Notification( arg_user, a.member_profile.user, message_str, self.project.get_absolute_url() )

    def set_team_accept( self ):
        self.team_accept = timezone.now()

    def set_member_accept( self ):
        self.member_accept = timezone.now()
        self.save()
        # дать доступ к repo
        self.project.add_repo_access()

    @classmethod
    def make_admin_after_project_create(cls, sender, instance, created, **kwargs):
        if created:
            project_created = instance
            project_created_user = project_created.created_user

            pm = cls( member_profile = project_created_user.profile, project=project_created, admin_flag = True, created_user = project_created.created_user, modified_user = project_created_user )
            pm.set_team_accept()
            pm.set_member_accept()

# http://stackoverflow.com/questions/25929165/create-model-after-group-has-been-created-django
post_save.connect(Member.make_admin_after_project_create, sender=Project)

@receiver(post_save, sender=Project)
def project_post_save_Notifier_Composer(sender, instance, **kwargs):
    # проект изменился - разослать уведомление всем участникам проекта - кроме автора изменений
    member_users = instance.GetFullMemberUsers().exclude( id = instance.modified_user.id )

    message_str = project_msg2json_str( MSG_NOTIFY_TYPE_PROJECT_CHANGED_ID, arg_project_name = instance.fullname )

    for mu in member_users:
        Send_Notification( instance.modified_user, mu, message_str, instance.get_absolute_url() )

def GetAllPublicProjectList( ):
    return Project.objects.filter( private_flag = False )

def GetMemberedProjectList( arg_user ):
    # если он не авторизован, то и членства ни в одном проекте нет
    if ( arg_user is None ) or ( not arg_user.is_authenticated ):
        return { }
    else:
        return Project.objects.filter( member__member_profile__user = arg_user ).order_by('-active_flag')

@reversion.register()
class Milestone(BaseStampedModel):
    project = models.ForeignKey(Project, on_delete=models.PROTECT, blank=False, null=False )
    fullname = models.CharField(max_length=255, verbose_name = 'Full name!', blank=False, null=False )
    planned_at = models.DateTimeField( blank=True, null=True )
    finished_at = models.DateTimeField( blank=True, null=True )

    def __str__(self):
        return self.fullname

    def get_absolute_url(self):
        return "/project/milestone/%i/" % self.id

def Get_Milestone_Report_for_Project( arg_project ):
    from django.db.models import Count, When, Case, IntegerField, F
    return Milestone.objects.filter(project = arg_project).order_by('finished_at').annotate(
               count_tasks=Count('task'),
               count_closed_tasks=Count( Case( When(task__finished_fact_at__isnull=False, then=F('task__pk')),
               output_field=IntegerField()
             )) )

@receiver(post_save, sender=Milestone)
def milestone_post_save_Notifier_Composer(sender, instance, **kwargs):
    # веха изменилась - разослать уведомление всем участникам проекта - кроме автора изменений
    member_users = instance.project.GetFullMemberUsers().exclude( id = instance.modified_user.id )
    message_str = project_msg2json_str( MSG_NOTIFY_TYPE_PROJECT_MILESTONE_CHANGED_ID, arg_project_name = instance.project.fullname, arg_milestone_name = instance.fullname )
    for mu in member_users:
        Send_Notification( instance.modified_user, mu, message_str, instance.get_absolute_url() )

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
    project = models.ForeignKey(Project, on_delete=models.PROTECT, blank=False, null=False )
    fullname = models.CharField(max_length=255, verbose_name = 'Full name!' )
    description = models.TextField(blank=True, null=True)
    # была мысль, что applicant - это тикет в Servicedesk от определенного клиента. Но если тикеты в SD будут отдельно, то достаточно и holder
    # applicant = models.ForeignKey( Profile, blank=True, null=True, related_name = "Applicant" )
    holder = models.ForeignKey(Profile, on_delete=models.PROTECT, blank=True, null=True, related_name = "Holder" )

    state = models.PositiveSmallIntegerField( blank=False, null=False, default = TASK_STATE_NEW )
    # 0 - новая задача
    milestone = models.ForeignKey(Milestone, on_delete=models.PROTECT, blank=True, null=True )
    finished_fact_at = models.DateTimeField( blank=True, null=True )
    important = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['-important']

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
            super(Task, self).save(*args, **kwargs) # Call the "real" save() method.
        else:
            raise Exception("Wrong milestone!")

    def get_absolute_url(self):
        return "/project/task/%i/" % self.id

    def description_html(self):
        return self.description

    def get_comments(self):
        return TaskComment.objects.filter( parenttask = self )

    def get_profiles(self):
        return TaskProfile.objects.filter( parenttask = self )

# связи между задачами
class TaskLink(models.Model):
    maintask=models.ForeignKey( Task, on_delete=models.PROTECT, related_name = 'main' )
    subtask=models.ForeignKey( Task, on_delete=models.PROTECT, related_name = 'sub' )
    class Meta:
        unique_together = ("maintask", "subtask")

    def get_absolute_url(self):
        return "/project/task_link/%i/" % self.id

@reversion.register()
class TaskComment(BaseStampedModel):
    parenttask = models.ForeignKey( Task, on_delete=models.PROTECT, null = False )
    comment = models.TextField(blank=False, null=False)

    def get_absolute_url(self):
        return "/project/task_comment/%i/" % self.id

    def __str__(self):
        # у коментария есть только длинный текст, поэтому выводить можно только реквизиты
        return str( self.created_user ) + " " + self.created_at.strftime("%Y-%m-%d %H:%M:%S")

    def comment_html(self):
        return self.comment

@reversion.register()
class TaskCheckList(BaseStampedModel):
    parenttask = models.ForeignKey( Task, on_delete=models.PROTECT, null = False, related_name = 'parenttask'  )
    checkname = models.CharField( max_length=255, blank=False, null=False )
    check_flag=models.BooleanField(blank=True, default=False)
    convertedtask = models.ForeignKey( Task, on_delete=models.PROTECT, default = None, null = True, related_name = 'convertedtask' )

    def get_absolute_url(self):
        return "/project/task_check/%i/" % self.id

    def __str__(self):
        return self.checkname

def GetTaskCommentators( arg_task, arg_exclude_user = None ):
    q = TaskComment.objects.values_list('created_user', flat = True).filter(parenttask = arg_task )
    if arg_exclude_user:
        q = q.exclude( created_user = arg_exclude_user )

    return User.objects.filter( id__in = q.distinct() )

def Send_Notifications_For_Task( arg_sender_user, arg_msg, arg_list, arg_url, arg_task_holder ):
    for m in arg_list:
        Send_Notification( arg_sender_user, m, arg_msg, arg_url )

    if not ( arg_task_holder is None ) and ( arg_task_holder != arg_sender_user ) and not ( arg_task_holder in arg_list ):
        Send_Notification( arg_sender_user, arg_task_holder, arg_msg, arg_url )

@receiver(post_save, sender=Task)
def task_post_save_Notifier_Composer(sender, instance, **kwargs):
    # задание изменилось - разослать уведомление всем участникам задания - кроме автора изменений

    task_users = GetTaskCommentators( instance, instance.modified_user )

    message_str = project_msg2json_str( MSG_NOTIFY_TYPE_PROJECT_TASK_CHANGED_ID, arg_project_name = instance.project.fullname, arg_task_name = instance.fullname )

    holder_user = None
    if ( not ( instance.holder is None ) ) and ( not ( instance.holder.user is None ) ):
        holder_user = instance.holder.user

    Send_Notifications_For_Task( instance.modified_user, message_str, task_users, instance.get_absolute_url(), holder_user )

@receiver(post_save, sender=TaskComment)
def taskcomment_post_save_Notifier_Composer(sender, instance, **kwargs):
    # Добавился (изменился) коментарий к задаче - разослать уведомление всем участникам задания - кроме автора изменений

    if kwargs['created'] :
        msg_type = MSG_NOTIFY_TYPE_PROJECT_TASK_NEW_COMMENT_ID
    else:
        msg_type = MSG_NOTIFY_TYPE_PROJECT_TASK_CHANGED_COMMENT_ID
    parent_task = instance.parenttask
    task_users = GetTaskCommentators( parent_task, instance.modified_user )

    message_str = project_msg2json_str( msg_type, arg_project_name = parent_task.project.fullname, arg_task_name = parent_task.fullname )

    parenttask_holder_user = None
    if ( not ( parent_task.holder is None ) ) and ( not ( parent_task.holder.user is None ) ):
        parenttask_holder_user = parent_task.holder.user

    Send_Notifications_For_Task( instance.modified_user, message_str, task_users, parent_task.get_absolute_url(), parenttask_holder_user )

def Get_User_Tasks( arg_user ):
    return None
    #return Task.objects.filter( state = TASK_STATE_NEW, assignee__user = arg_user )

# участники-ресурсы на задачу
class TaskProfile(BaseStampedModel):
    parenttask=models.ForeignKey( Task, on_delete=models.PROTECT, related_name = 'profile2task' )
    profile=models.ForeignKey( Profile, on_delete=models.PROTECT, related_name = 'task2profile' )
    class Meta:
        unique_together = ("parenttask", "profile")

@receiver(post_save, sender=TaskProfile)
def taskprofile_post_save_Notifier_Composer(sender, instance, **kwargs):
    # профиль назначен на задачу
    assigned_profile = instance.profile
    if assigned_profile.profile_type == PROFILE_TYPE_USER:
        task = instance.parenttask

        holder_user = None
        if ( not ( task.holder is None ) ) and ( not ( task.holder.user is None ) ):
            holder_user = task.holder.user

        if assigned_profile.user != holder_user:
            message_str = project_msg2json_str( MSG_NOTIFY_TYPE_PROJECT_TASK_ASSIGNED_ID, arg_project_name = task.project.fullname, arg_task_name = task.fullname )
            Send_Notification( holder_user, assigned_profile.user, message_str, task.get_absolute_url() )

def Get_Profiles_Available2Task( arg_task_id ):
    p = Task.objects.get( pk=arg_task_id ).project
    #только принявшие приглашение и на назначенные + неназначенные не пользователи (организации и проч)
    q = ( ( p.GetFullMemberProfiles() | Profile.objects.filter( profile_type__in = PROFILE_TYPE_FOR_TASK ) ).distinct() ).exclude( task2profile__parenttask = arg_task_id )
    return q

def Get_Profile_Tasks( arg_profile ):
    return Task.objects.filter( profile2task__profile = arg_profile )
