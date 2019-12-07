import django_filters

from project.models import Project, Task, GetMemberedProjectList, TASK_STATE_LIST_CHOICES

from ich_bau.profiles.models import Profile, PROFILE_TYPE_USER, PROFILE_TYPE_FOR_TASK

# https://django-filter.readthedocs.io/en/latest/guide/usage.html

class ProjectFilter(django_filters.FilterSet):

    fullname = django_filters.CharFilter( lookup_expr='icontains')
    description = django_filters.CharFilter( lookup_expr='icontains')

    class Meta:
        model = Project
        fields = ['fullname', 'description' ]

class TaskFilter(django_filters.FilterSet):

    fullname = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    state = django_filters.ChoiceFilter(choices=TASK_STATE_LIST_CHOICES)

    class Meta:
        model = Task
        fields = [ 'fullname', 'description', 'state', 'milestone', 'holder', 'kind', 'profile2task__profile', 'task2domain__taskdomain' ]
    
    def __init__(self, *args , **kwargs ):
        super(TaskFilter, self).__init__( *args , **kwargs )
        self.filters['profile2task__profile'].label = 'Assigned'
        self.filters['task2domain__taskdomain'].label = 'Domain'

def user_projects(request):
    if request is None:
        return Project.objects.none()

    return GetMemberedProjectList( request.user )

class TaskFilter_for_Linking(django_filters.FilterSet):
    fullname = django_filters.CharFilter(lookup_expr='icontains')
    state = django_filters.ChoiceFilter(choices=TASK_STATE_LIST_CHOICES )
    project = django_filters.ModelChoiceFilter( queryset= user_projects )

    class Meta:
        model = Task
        fields = ['fullname', 'state', 'project' ]

