from django.contrib.auth.models import User
from .models import *

from django.test import TestCase

TEST_MAIN_ORG_NAME = 'Main org'

class Profile_Test(TestCase):
    def setUp(self):
        self.main_org_profile = Profile( profile_type = PROFILE_TYPE_ORG )
        self.main_org_profile.name = TEST_MAIN_ORG_NAME
        self.main_org_profile.save()

    def test_Org_profile_type(self):
        self.assertEqual( self.main_org_profile.profile_type, PROFILE_TYPE_ORG )

        
