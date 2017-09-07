import django_filters

from project.models import Project, Task, TASK_STATE_LIST_CHOICES

class ProjectFilter(django_filters.FilterSet):
    
    fullname = django_filters.CharFilter(lookup_type='icontains')
    description = django_filters.CharFilter(lookup_type='icontains')
    
    class Meta:
        model = Project
        fields = ['fullname', 'description' ]

class TaskFilter(django_filters.FilterSet):
    
    fullname = django_filters.CharFilter(lookup_type='icontains')
    description = django_filters.CharFilter(lookup_type='icontains')    
    state = django_filters.ChoiceFilter(choices=TASK_STATE_LIST_CHOICES)
    
    class Meta:
        model = Task
        fields = ['fullname', 'description', 'state', 'milestone', 'resource' ]
      
