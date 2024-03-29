﻿# project forms

from django import forms
from project.models import Project, PROJECT_VISIBLE_LIST_CHOICES, PROJECT_VISIBLE_PRIVATE, Task, TaskComment, Milestone, Member, TaskDomain, TaskLink, TaskProfile, TASK_PROFILE_PRIORITY_LIST, TASK_PROFILE_PRIORITY_INTERESTED, TASK_PROFILE_PRIORITY_LIST_CHOICES, TaskCheckList, Task2Domain, Get_Profiles_Available2Task, Sub_Project, Task_Property_Amount
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
        fields = ['fullname', 'private_type', 'active_flag', 'use_sub_projects', 'use_properties', 'description' ]

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
        fields = ['fullname', 'description', 'milestone', 'holder', 'important', 'kind', 'sub_project' ]

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        # форма работает в 2х режимах - создания (смотрим 'initial') и редактирования (смотрим 'instance') свойства.
        instance = kwargs.pop('instance', None)
        if (instance is None):
            pop = kwargs.pop('initial', None)
            p = pop['project']
        else:
            p = instance.project

        # отображать вехи, подпроекты и пользователей только этого проекта
        if not ( p is None):
            self.fields['milestone'].queryset = Milestone.objects.filter( project = p, finished_at__isnull = True )
            if p.use_sub_projects:
                self.fields['sub_project'].queryset = Sub_Project.objects.filter( project = p )
            else:
                self.fields['sub_project'].widget = HiddenInput()

            list = p.GetFullMemberProfiles()
            self.fields['holder'].queryset = list

class TaskLinkedForm(forms.ModelForm):
    subtasks=forms.ModelMultipleChoiceField( Task.objects, help_text="subtask", required=True, widget=CheckboxSelectMultiple() )

    def __init__(self, *args, **kwargs):
        arg_qs = kwargs.pop('arg_qs', None)
        super(TaskLinkedForm, self).__init__(*args, **kwargs)

        if ( arg_qs != "" ):
            self.fields['subtasks'].queryset = arg_qs

    class Meta:
        model = TaskLink
        fields = ['subtasks']

class TaskProfileForm(forms.ModelForm):
    profile=forms.ModelChoiceField( Profile.objects,
                                    help_text="profile",
                                    widget=forms.RadioSelect,
                                    required=True )
    # forms.BooleanField( label = 'Responsible', help_text="Responsible or interested", required=False )
    priority=forms.ChoiceField( label='Priority',
                                      widget=forms.RadioSelect,
                                      choices=TASK_PROFILE_PRIORITY_LIST_CHOICES,
                                      initial = TASK_PROFILE_PRIORITY_INTERESTED )

    def __init__(self, *args, **kwargs):
        argmaintaskid = kwargs.pop('argmaintaskid', None)
        q = kwargs.pop('arg_query_for_combo', None)
        super(TaskProfileForm, self).__init__(*args, **kwargs)
        self.fields['profile'].queryset = q

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


class Sub_ProjectForm(forms.ModelForm):
    class Meta:
        model = Sub_Project
        fields = ['fullname',  ]

class Task_Property_Amount_Form(forms.ModelForm):

    class Meta:
        model = Task_Property_Amount
        fields = [ 'property', 'amount' ]

    def __init__(self, *args, **kwargs):
        allowed_properties = kwargs.pop('arg_allowed_properties', None)
        super(Task_Property_Amount_Form, self).__init__(*args, **kwargs)

        if allowed_properties is None:
            self.fields['property'].widget = HiddenInput()
        else:
            self.fields['property'].queryset = allowed_properties
