from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView

from django.contrib import admin

from .profiles.views import ProfileCreateView, ProfileDetailView, my_profile_view, ProfileEditView, ProfileListView, notifications_view_unread, notifications_view_read, notification_read

urlpatterns = [
    url(r"^$", TemplateView.as_view(template_name="homepage.html"), name="home"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/", include("account.urls")),

    url(r"^profile/view/", my_profile_view, name="my_profile_view"),
    url(r"^profile/edit/", ProfileEditView.as_view(), name="profiles_edit"),
    url(r"^p/$", ProfileListView.as_view(), name="profiles_list"),
    url(r"^p/(?P<pk>\w+)/$", ProfileDetailView.as_view(), name="profiles_detail"),
    url(r"^p/create$", ProfileCreateView.as_view(), name="profile_create"),

    url(r"^notifications/$", notifications_view_unread, name="unread_notifications_view"),
    url(r"^notifications/read/$", notifications_view_read, name="read_notifications_view"),
    url(r"^notification/(?P<notification_id>\w+)/$", notification_read, name="notification_read"),

    url(r"^project/", include('project.urls', namespace="project") ),
    url(r"^crm/", include('crm.urls', namespace="crm") ),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)