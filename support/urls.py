from django.conf.urls import url

from support import views

app_name = 'support'

urlpatterns = [

    url(r'^$', views.index, name='index'),

    ]