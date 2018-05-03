from django.contrib.auth.models import User
from .models import *

from django.test import TestCase

TEST_MAIN_ORG_NAME = 'Main org'

class Profile_Test(TestCase):
    def setUp(self):
        self.main_org_profile = Profile( profile_type = PROFILE_TYPE_ORG )
        self.main_org_profile.name = TEST_MAIN_ORG_NAME
        self.main_org_profile.save()
        
        for i in ( 'a', 'b', 'c' ):
            sub_dep_profile = Profile( profile_type = PROFILE_TYPE_DEPARTAMENT )
            sub_dep_profile.name = i
            sub_dep_profile.save()
            r = Profile_Affiliation( main_profile=self.main_org_profile, sub_profile=sub_dep_profile )
            r.save()

    def test_Org_profile_type(self):
        self.assertEqual( self.main_org_profile.profile_type, PROFILE_TYPE_ORG )
        self.assertEqual( Profile_Affiliation.objects.filter(main_profile=self.main_org_profile).count(), 3 )