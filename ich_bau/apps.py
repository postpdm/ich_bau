from importlib import import_module

from django.apps import AppConfig as BaseAppConfig

class AppConfig(BaseAppConfig):

    name = "ich_bau"

    def ready(self):
        import_module("ich_bau.receivers")
        import_module("ich_bau.profiles.receivers")
        import_module("project")