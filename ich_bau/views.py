# views
from django.shortcuts import render
from django.template import RequestContext

from django.apps import apps

from commons.apps import BaseAppConfig


def get_homepage( request ):

    #context = RequestContext(request)

    blocks = ''
    for a in apps.get_app_configs():
        if hasattr( a, 'get_site_index_html_block' ):
            blocks = blocks + a.get_site_index_html_block( request )
    
    context_dict = { 'apps_html_blocks' : blocks }
    
    # —формировать ответ, отправить пользователю
    return render( request, 'homepage.html', context_dict )