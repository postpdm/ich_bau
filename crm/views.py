from django.core.urlresolvers import reverse
from django.views.generic import UpdateView, DetailView, ListView, CreateView

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template import RequestContext

from account.mixins import LoginRequiredMixin

from .models import *
from .forms import *
from account.decorators import login_required
from reversion.models import Version

from django.db import transaction
import reversion
from django.contrib import messages

class ContractListView(ListView):
    model = Contract
    context_object_name = "contracts"

class ContractCreateView(LoginRequiredMixin, CreateView):
    form_class = ContractForm
    model = Contract

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.set_change_user(self.request.user)

        with transaction.atomic(), reversion.create_revision():
            reversion.set_user(self.request.user)
            self.object.save()

        messages.success(self.request, "You successfully create the contract!")
        return HttpResponseRedirect(self.get_success_url())

def contract_view(request, contract_id):
    contract = get_object_or_404( Contract, pk=contract_id)
    context = RequestContext(request)
    context_dict = { 'contract': contract,
                         }
    # Рендерить ответ
    return render( request, 'crm/contract.html', context_dict )

@login_required
def contract_edit(request, contract_id):
    context = RequestContext(request)

    contract = get_object_or_404( Contract, pk=contract_id )

    if request.method == 'POST':
        form = ContractForm(request.POST, instance=contract)

        if form.is_valid():
            contract.set_change_user(request.user)
            with transaction.atomic(), reversion.create_revision():
                reversion.set_user(request.user)
                form.save()

            # перебросить пользователя на просмотр
            messages.success(request, "You successfully updated this contract!")
            return HttpResponseRedirect( contract.get_absolute_url() )
        else:
            print( form.errors )
    else:
        form = ContractForm( instance=contract )

    return render(  request, 'crm/contract_form.html',
            {'form': form, 'contract':contract},
             context)

def contract_history(request, contract_id):
    context = RequestContext(request)
    contract = get_object_or_404( Contract, pk=contract_id)

    versions = Version.objects.get_for_object( contract )

    context_dict = { 'contract': contract,
                     'versions': versions }
    # Рендерить ответ
    return render( request, 'crm/contract_history.html', context_dict )