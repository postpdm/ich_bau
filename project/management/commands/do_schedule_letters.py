from django.core.management.base import BaseCommand

from django.utils import timezone


class Command(BaseCommand):
    help = 'do schedule letters sending'

    def handle(self, *args, **options):
        from django.contrib.auth.models import User
        
        users = User.objects.filter( is_active = True )
        print( users )
        
        for u in users:
            print( u )
        
        