from django.conf.urls import url

from crm import views

urlpatterns = [

    url(r'^$', views.ContractListView.as_view(), name="contracts_list"),

    ]