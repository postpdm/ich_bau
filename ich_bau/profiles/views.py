from django.core.urlresolvers import reverse
from django.views.generic import CreateView, UpdateView, DetailView, ListView

from django.contrib import messages

from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext

from account.mixins import LoginRequiredMixin

from .forms import ProfileForm, ContactProfileForm
from .models import *
from account.decorators import login_required
from reversion.models import Version

class ProfileEditView(LoginRequiredMixin, UpdateView):

    form_class = ProfileForm
    model = Profile

    def get_object(self):
        return self.request.user.profile

    def get_success_url(self):
        return reverse( my_profile_view )

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
            from project.repo_wrapper import Decrypt_Repo_User_PW
            context['user_repo_pw'] = Decrypt_Repo_User_PW( current_profile.repo_pw )

        context['main_profiles'] = Profile_Affiliation.objects.filter( sub_profile = current_profile )
        context['sub_profiles'] =  Profile_Affiliation.objects.filter( main_profile = current_profile )
        if ( current_profile.profile_type == PROFILE_TYPE_USER ) and ( not( current_profile.user is None ) ):
            context['controlled_profiles'] = Profile_Control_User.objects.filter( control_user = current_profile.user )
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
