from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView, ListView

from django.contrib import messages

from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext

from account.mixins import LoginRequiredMixin

from .forms import ProfileForm, ContactProfileForm, Profile_AffiliationForm
from .models import *
from account.decorators import login_required
from reversion.models import Version
from django.http import HttpResponseRedirect, Http404
from project.models import Get_User_Tasks

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
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        current_profile = self.get_object()
        if current_profile.user == self.request.user:
            # юзер смотрит свой собственный профиль
            context['user_repo_pw'] = current_profile.repo_pw

        context['main_profiles'] = current_profile.main_profiles()
        context['sub_profiles'] =  current_profile.sub_profiles()
        if ( current_profile.profile_type == PROFILE_TYPE_USER ) and ( not( current_profile.user is None ) ):
            context['controlled_profiles'] = Profile_Control_User.objects.filter( control_user = current_profile.user )
            context['user_tasks'] = Get_User_Tasks( current_profile.user )
        context['controlled_by_user'] = Profile_Control_User.objects.filter( controlled_profile = current_profile )

        return context

@login_required
def my_profile_view(request):
    return redirect( 'profiles_detail', pk = request.user.profile.id )

class ProfileListView(ListView):

    model = Profile
    context_object_name = "profiles"

class ProfileCreateView(LoginRequiredMixin, CreateView):
    model = Profile
    form_class = ContactProfileForm

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

@login_required
def notifications_view_prepare(request, arg_new):
    context = RequestContext(request)
    u = request.user
    if u is None:
        raise Http404

    notifications = GetUserNoticationsQ( u, arg_new )

    context_dict = { 'notifications' : notifications, 'filter_new' : arg_new }
    return render( request, 'profiles/notifications.html', context_dict )

@login_required
def notifications_view_unread(request):
    return notifications_view_prepare( request, True )

@login_required
def notifications_view_read(request):
    return notifications_view_prepare( request, False )

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
        Http404
