# common utils
from django.contrib.sites.models import Site
from django.conf import settings

def get_full_site_url():
    return settings.BASE_PROTOKOL + '://' + Site.objects.get_current().domain