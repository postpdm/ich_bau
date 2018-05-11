from django.conf.urls import url

from crm import views
app_name = 'crm'

urlpatterns = [
    url(r'^$', views.ContractListView.as_view(), name="contracts_list"),

    url(r'^contract_add/$', views.ContractCreateView.as_view(), name='contract_add'),
    url(r'^contract/(?P<contract_id>\w+)/$', views.contract_view, name='contract_view'),
    url(r'^contract/(?P<contract_id>\w+)/contract_edit/$', views.contract_edit, name='contract_edit'),
    url(r'^contract/(?P<contract_id>\w+)/history/$', views.contract_history, name='contract_history'),
    ]
