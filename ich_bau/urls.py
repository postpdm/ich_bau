from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

from django.contrib import admin

from .views import get_homepage

from .profiles.views import ProfileCreateView, ProfileCreateSubView, ProfileDetailView, ProfileUpdateView, my_profile_view, ProfileEditView, ProfileListView, notifications_view_unread, notifications_view_unread_by_type, notifications_view_read, notification_read

urlpatterns = [
    url(r"^$", get_homepage, name="home"),
    url(r"^admin/", admin.site.urls),
    url(r"^account/", include("account.urls")),
    url(r'^summernote/', include('django_summernote.urls')),

    url(r"^profile/view/", my_profile_view, name="my_profile_view"),
    url(r"^profile/edit/", ProfileEditView.as_view(), name="profiles_edit"),
    url(r"^p/$", ProfileListView.as_view(), name="profiles_list"),
    url(r"^p/(?P<pk>\w+)/$", ProfileDetailView.as_view(), name="profiles_detail"),
    url(r"^p/(?P<pk>\w+)/edit/$", ProfileUpdateView.as_view(), name="profile_update"),
    url(r"^p/create$", ProfileCreateView.as_view(), name="profile_create"),
    url(r"^p/(?P<pk>\w+)/add_sub/$", ProfileCreateSubView.as_view(), name="profile_add_sub"),
    url(r"^p/(?P<pk>\w+)/level/(?P<level_pk>\w+)/add_sub/$", ProfileCreateSubView.as_view(), name="profile_add_sub_tree_view"),

    url(r"^notifications/$", notifications_view_unread, name="unread_notifications_view"),
    url(r"^notifications_by_type/$", notifications_view_unread_by_type, name="unread_notifications_view_by_type"),
    url(r"^notifications/read/$", notifications_view_read, name="read_notifications_view"),
    url(r"^notification/(?P<notification_id>\w+)/$", notification_read, name="notification_read"),

    url(r"^support/", include('support.urls', namespace="support") ),
    url(r"^project/", include('project.urls', namespace="project") ),
    url(r"^crm/", include('crm.urls', namespace="crm") ),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)