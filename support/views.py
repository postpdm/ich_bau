from django.shortcuts import render

from .models import SupportProject

# Create your views here.

def index( request ):
    sp = SupportProject.objects.all()
    context_dict = { 'sps' : sp,  }
    return render( request, 'support/index.html', context_dict )
