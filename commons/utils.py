# common utils
from django.contrib.sites.models import Site

def get_full_site_url():
    return Site.objects.get_current().domain