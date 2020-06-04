from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView, ListView

from django.contrib import messages

from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext

from account.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin

from .forms import ProfileForm, ContactProfileForm, Profile_AffiliationForm
from .models import *
from account.decorators import login_required
from reversion.models import Version
from django.http import HttpResponseRedirect, Http404
from project.models import Get_User_Tasks, Get_Profile_Tasks, GetAvailableProjectList, GetMemberedProjectList

class ProfileEditView(LoginRequiredMixin, UpdateView):

    form_class = ProfileForm
    model = Profile

    def get_object(self):
        return self.request.user.profile

    def get_success_url(self):
        return reverse_lazy( my_profile_view )

    def form_valid(self, form):
        response = super(ProfileEditView, self).form_valid(form)
        messages.success(self.request, "You successfully updated your profile.")
        return response

class ProfileDetailView(DetailView):

    model = Profile
    slug_url_kwarg = "profile_id"
    slug_field = "id"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        Current_User_Profile = False
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        current_profile = self.get_object()
        profile_is_managed = False
        view_projects_and_tasks_header = ''
        profile_tasks = None
        profile_projects = None

        # affiliated profiles
        context['main_profiles'] = current_profile.main_profiles()
        context['sub_profiles'] =  current_profile.sub_profiles()

        if ( current_profile.profile_type == PROFILE_TYPE_USER ) and ( not( current_profile.user is None ) ):
            context['managed_profiles'] = Profile_Manage_User.objects.filter( manager_user = current_profile.user )
            context['managed_by_user'] = Profile_Manage_User.objects.filter( managed_profile = current_profile )

            if self.request.user == current_profile.user:
                # юзер смотрит свой собственный профиль
                context['user_repo_pw'] = current_profile.repo_pw
                Current_User_Profile = True
                view_projects_and_tasks_header = 'Projects and tasks assigned to you'
                profile_tasks = Get_User_Tasks( self.request.user )
                profile_projects = GetMemberedProjectList( self.request.user )
        if not profile_tasks:
            profile_is_managed = Is_User_Manager( self.request.user, current_profile )
            if profile_is_managed:
                profile_tasks = Get_User_Tasks( current_profile.user )

                if current_profile.has_account:
                    profile_projects = GetMemberedProjectList( current_profile.user )

                view_projects_and_tasks_header = 'Projects and tasks assigned to managed profiles'
            else:
                profile_tasks = Get_Profile_Tasks( current_profile ).filter( project__in = GetAvailableProjectList( self.request.user ) )

                if current_profile.has_account:
                    profile_projects = GetMemberedProjectList( current_profile.user ).distinct() & GetAvailableProjectList( self.request.user )

                view_projects_and_tasks_header = 'Projects and tasks assigned to profile (for projects available for you)'

        context['current_user_profile'] = Current_User_Profile
        context['view_projects_and_tasks_header'] = view_projects_and_tasks_header
        context['profile_tasks'] = profile_tasks
        context['profile_projects'] = profile_projects

        return context

@login_required
def my_profile_view(request):
    return redirect( 'profiles_detail', pk = request.user.profile.id )

class ProfileListView(ListView):

    model = Profile
    context_object_name = "profiles"

    def get_context_data(self, **kwargs):
        context = super(ProfileListView, self).get_context_data(**kwargs)
        # check if user has permission to create profile (or super user)
        context[ 'can_add_profile' ] = self.request.user.has_perm('profiles.add_profile')
        return context

class ProfileCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Profile
    form_class = ContactProfileForm
    permission_required = 'profiles.add_profile'
    raise_exception = True

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ContactProfileForm

class ProfileCreateSubView(LoginRequiredMixin, CreateView):
    model = Profile_Affiliation
    form_class = Profile_AffiliationForm

    def get_initial(self):
        try:
            self.mp = get_object_or_404( Profile, pk = self.kwargs['pk'])
            return { 'main_profile': self.mp, }
        except:
            Http404()

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.main_profile = self.mp
        self.object.save()

        messages.success(self.request, "You successfully add the affiliation!")
        return HttpResponseRedirect( self.object.main_profile.get_absolute_url() )

from .models import Notification, GetUserNoticationsQ

VIEW_NOTIFICATIONS_NEW_BY_USER = 1
VIEW_NOTIFICATIONS_NEW_BY_TYPE = 2
VIEW_NOTIFICATIONS_OLD         = 3

@login_required
def notifications_view_prepare(request, arg_kind):
    context = RequestContext(request)
    u = request.user
    if u is None:
        raise Http404

    OLD_NOTIFICATIONS_VIEW_LIMIT = 20
    filter_name = ''

    if arg_kind == VIEW_NOTIFICATIONS_NEW_BY_USER:
        notifications = GetUserNoticationsQ( u, True ).order_by('sender_user', '-created_at' )
        filter_name = 'new_by_user'
    else:
        if arg_kind == VIEW_NOTIFICATIONS_NEW_BY_TYPE:
            notifications = GetUserNoticationsQ( u, True ).order_by(  'content_type', 'object_id', '-created_at' )
            filter_name = 'new_by_type'
        else:
            if arg_kind == VIEW_NOTIFICATIONS_OLD:
                notifications = GetUserNoticationsQ( u, False ).order_by('-created_at')[:OLD_NOTIFICATIONS_VIEW_LIMIT]
                filter_name = 'old'
            else:
                raise Http404

    context_dict = { 'notifications' : notifications, 'filter_name' : filter_name, 'OLD_NOTIFICATIONS_VIEW_LIMIT' : OLD_NOTIFICATIONS_VIEW_LIMIT }
    return render( request, 'profiles/notifications.html', context_dict )

@login_required
def notifications_view_unread(request):
    return notifications_view_prepare( request, VIEW_NOTIFICATIONS_NEW_BY_USER )

@login_required
def notifications_view_unread_by_type(request):
    return notifications_view_prepare( request, VIEW_NOTIFICATIONS_NEW_BY_TYPE )

@login_required
def notifications_view_read(request):
    return notifications_view_prepare( request, VIEW_NOTIFICATIONS_OLD )

@login_required
def notification_read( request, notification_id ):
    from django.http import HttpResponse
    # у самого уведомления отдельной страницы нет
    n = get_object_or_404( Notification, pk=notification_id )
    # убедимся, что юзер - адресат уведомления
    if n.reciever_user == request.user:
        if n.get_unreaded:
            n.mark_readed()

        if ( n.msg_url is None ) or ( n.msg_url == '' ):
            return redirect( 'unread_notifications_view' )
        else:
            return redirect( n.msg_url )
    else:
        raise Http404()
