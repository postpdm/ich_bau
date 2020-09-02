from commons.apps import BaseAppConfig

class AppConfig(BaseAppConfig):
    name = 'project'

    def get_site_index_html_block( self, request ):

        from project.models import GetMemberedProjectList
        if request.user.is_authenticated:
            html = ''
            projects = GetMemberedProjectList(request.user)
            for p in projects:
                html = html + '<li> <a href="' + p.get_absolute_url() + '">' + p.fullname + '</a></li>'
            if html:
                html = '<p>Your projects</p><ul>' + html + '</ul>'
            return html
        else:
            return ''
