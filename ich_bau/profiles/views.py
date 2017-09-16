from django.core.urlresolvers import reverse
from django.views.generic import UpdateView, DetailView, ListView

from django.contrib import messages

from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext

from account.mixins import LoginRequiredMixin

from .forms import ProfileForm
from .models import Profile
from account.decorators import login_required
from reversion.models import Version

class ProfileEditView(LoginRequiredMixin, UpdateView):

    form_class = ProfileForm
    model = Profile

    def get_object(self):
        return self.request.user.profile

    def get_success_url(self):
        return reverse("profiles_list")

    def form_valid(self, form):
        response = super(ProfileEditView, self).form_valid(form)
        messages.success(self.request, "You successfully updated your profile.")
        return response


class ProfileDetailView(DetailView):

    model = Profile
    slug_url_kwarg = "username"
    slug_field = "user__username"
    context_object_name = "profile"


class ProfileListView(ListView):

    model = Profile
    context_object_name = "profiles"

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

class ProfileDetailView(DetailView):

    model = Profile
    slug_url_kwarg = "username"
    slug_field = "user__username"
    context_object_name = "profile"
    def get_context_data(self, **kwargs):
        
        import datetime        
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        
        contribution_list = Version.objects.filter( revision__user = context['profile'].user, content_type__in = Contribution_Models ).order_by('-id').prefetch_related('object')
        
        paginator = Paginator(contribution_list, PAGINATOR_OBJECTS_PER_PAGE )
        page = self.request.GET.get('page')
        
        try:
            contributions = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            contributions = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            contributions = paginator.page(paginator.num_pages)        
        
        context['contributions'] = contributions
        # https://github.com/etianen/django-reversion/issues/353#issuecomment-56173067 посоветовал использовать prefetch_related
        return context