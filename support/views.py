from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect

from .models import SupportProject

# Create your views here.

def index( request ):
    sp = SupportProject.objects.all()
    
    if sp.count() == 1:
        return HttpResponseRedirect( sp.first().project.get_absolute_url() )
    else:
        context_dict = { 'sps' : sp,  }
        return render( request, 'support/index.html', context_dict )
