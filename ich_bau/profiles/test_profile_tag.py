from django.test import TestCase
from .templatetags.profile_tag import *

class Profile_Tag_Test(TestCase):
    def test_profile_type_name(self):
        self.assertEqual( profile_type_name( None, 0), 'Bot' )
        self.assertEqual( profile_type_name( None, 1), 'User' )
        self.assertEqual( profile_type_name( None, 2), 'People' )
        self.assertEqual( profile_type_name( None, 3), 'Departament' )
        self.assertEqual( profile_type_name( None, 4), 'Organization' )
        self.assertEqual( profile_type_name( None, 5), 'Resource' )
        
        self.assertEqual( profile_type_name( None, 6), None )