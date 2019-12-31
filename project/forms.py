# project forms

from django import forms
from project.models import Project, PROJECT_VISIBLE_LIST_CHOICES, PROJECT_VISIBLE_PRIVATE, Task, TaskComment, Milestone, Member, TaskDomain, TaskLink, TaskProfile, TaskCheckList, Task2Domain, Get_Profiles_Available2Task
from ich_bau.profiles.models import PROFILE_TYPE_USER

from django.forms.widgets import HiddenInput, CheckboxSelectMultiple
from mptt.forms import TreeNodeChoiceField

from commons.editors import DateTime_Field, TextEditor_Field

class ProjectForm(forms.ModelForm):
    description = TextEditor_Field(arg_required=False)
    # https://docs.djangoproject.com/en/2.2/ref/forms/api/#dynamic-initial-values
    # https://docs.djangoproject.com/en/2.2/ref/forms/widgets/#widgets-inheriting-from-the-select-widget
    private_type = forms.ChoiceField( label='Project visible level',
                                      widget=forms.RadioSelect,
                                      choices=PROJECT_VISIBLE_LIST_CHOICES,
                                      initial = PROJECT_VISIBLE_PRIVATE )

    class Meta:
        model = Project
        fields = ['fullname', 'private_type', 'active_flag', 'description' ]

class MilestoneForm(forms.ModelForm):
    planned_at = DateTime_Field( False )
    finished_at = DateTime_Field( False )

    class Meta:
        model = Milestone
        fields = ['fullname', 'planned_at', 'finished_at' ]

from ich_bau.profiles.models import Profile, Get_Users_Profiles

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['member_profile', 'admin_flag' ]

    def __init__(self, *args, **kwargs):
        super(MemberForm, self).__init__(*args, **kwargs)
        # форма работает в режиме создания (смотрим 'initial')
        p = kwargs.pop('initial', None)['project']

        # отображать только свободных людей
        if not ( p is None):
            self.fields['member_profile'].queryset = Get_Users_Profiles().exclude( member_profile__project_id = p.id )

class TaskForm(forms.ModelForm):
    description = TextEditor_Field(arg_required=False)

    class Meta:
        model = Task
        fields = ['fullname', 'description', 'milestone', 'holder', 'important', 'kind', ]

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        # форма работает в 2х режимах - создания (смотрим 'initial') и редактирования (смотрим 'instance') свойства.
        instance = kwargs.pop('instance', None)
        if (instance is None):
            pop = kwargs.pop('initial', None)
            p = pop['project']
        else:
            p = instance.project

        # отображать вехи и пользователей только этого проекта
        if not ( p is None):
            self.fields['milestone'].queryset = Milestone.objects.filter( project = p, finished_at__isnull = True )
            list = p.GetFullMemberProfiles()
            self.fields['holder'].queryset = list

class TaskLinkedForm(forms.ModelForm):
    subtasks=forms.ModelMultipleChoiceField( Task.objects, help_text="subtask", required=True, widget=CheckboxSelectMultiple() )

    def __init__(self, *args, **kwargs):
        arg_qs = kwargs.pop('arg_qs', None)
        super(TaskLinkedForm, self).__init__(*args, **kwargs)

        self.fields['subtasks'].queryset = arg_qs

        if ( arg_qs != "" ):
            self.fields['subtasks'].queryset = arg_qs

    class Meta:
        model = TaskLink
        fields = ['subtasks']

class TaskProfileForm(forms.ModelForm):
    profile=forms.ModelChoiceField( Profile.objects, help_text="profile", required=True )
    priority=forms.BooleanField( label = 'Responsible', help_text="Responsible or interested", required=False )

    def __init__(self, *args, **kwargs):
        argmaintaskid = kwargs.pop('argmaintaskid', None)
        add_user = kwargs.pop('add_user', None)
        super(TaskProfileForm, self).__init__(*args, **kwargs)

        if (argmaintaskid != "" ):
            main_task = Task.objects.get( id = argmaintaskid )
            q = Get_Profiles_Available2Task( argmaintaskid ) # base query - all types profiles, unassigned
            if add_user:
                self.fields['profile'].queryset = q.filter( profile_type = PROFILE_TYPE_USER ) # only users
            else:
                self.fields['profile'].queryset = q.exclude( profile_type = PROFILE_TYPE_USER ) # all except users

    class Meta:
        model = TaskProfile
        fields = ['profile', 'priority' ]

class TaskDomainForm(forms.ModelForm):
    taskdomain = TreeNodeChoiceField(queryset=TaskDomain.objects.all())

    def __init__(self, *args, **kwargs):
        argmaintaskid = kwargs.pop('argmaintaskid', None)
        super(TaskDomainForm, self).__init__(*args, **kwargs)

        if (argmaintaskid != "" ):
            #main_task = Task.objects.get( id = argmaintaskid )
            self.fields['taskdomain'].queryset = TaskDomain.objects.all().exclude( domain2task__task = argmaintaskid )

    class Meta:
        model = Task2Domain
        fields = ['taskdomain']

class TaskCommentForm(forms.ModelForm):
    comment = TextEditor_Field()

    class Meta:
        model = TaskComment
        fields = ['comment' ]

class TaskCheckListForm(forms.ModelForm):
    class Meta:
        model = TaskCheckList
        fields = ['checkname', 'check_flag' ]