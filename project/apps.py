from commons.apps import BaseAppConfig
from django.template.loader import render_to_string

class AppConfig(BaseAppConfig):
    name = 'project'

    def get_site_index_html_block( self, request ):
        from project.models import GetMemberedProjectList
        if request.user.is_authenticated:

            projects = GetMemberedProjectList(request.user)
            return render_to_string( 'project/site_index_project_list.html', { 'projects' : projects } )
        else:
            return ''
