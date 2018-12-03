from django.test import TestCase
from .templatetags.profile_tag import *

class Profile_Tag_Test(TestCase):
    def test_fa_profile_icon(self):
        self.assertTrue( 'fa-meh-o' in fa_profile_icon( None, 0) )
        self.assertTrue( 'fa-user' in fa_profile_icon( None, 1) )
        self.assertTrue( 'fa-bars' in fa_profile_icon( None, 2) )
        self.assertTrue( 'fa-users' in fa_profile_icon( None, 3) )
        self.assertTrue( 'fa-university' in fa_profile_icon( None, 4) )
        self.assertTrue( 'fa-cogs' in fa_profile_icon( None, 5) )
        self.assertEqual( fa_profile_icon( None, 6), None )
        self.assertEqual( fa_profile_icon( None, None), None )       
    
    def test_profile_type_name(self):
        self.assertEqual( profile_type_name( None, 0), 'Bot' )
        self.assertEqual( profile_type_name( None, 1), 'User' )
        self.assertEqual( profile_type_name( None, 2), 'People' )
        self.assertEqual( profile_type_name( None, 3), 'Departament' )
        self.assertEqual( profile_type_name( None, 4), 'Organization' )
        self.assertEqual( profile_type_name( None, 5), 'Resource' )
        
        self.assertEqual( profile_type_name( None, 6), None )
        self.assertEqual( profile_type_name( None, None), None )