# base app for pluggable aaplications
from django.apps import AppConfig

class BaseAppConfig(AppConfig):

    def get_site_index_html_block( self, request ):
        pass
