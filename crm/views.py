from django.core.urlresolvers import reverse
from django.views.generic import UpdateView, DetailView, ListView

from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext

from account.mixins import LoginRequiredMixin

from .models import *
from account.decorators import login_required
from reversion.models import Version

class ContractListView(ListView):

    model = Contract
    context_object_name = "contracts"