from django.contrib.auth.models import User
from .models import *

from django.test import TestCase

TEST_MAIN_ORG_NAME = 'Main org'

SUB_ORG_NAMES_LIST = ( 'a', 'b', 'c', 'd' )

class Profile_Test(TestCase):
    def setUp(self):
        self.main_org_profile = Profile( profile_type = PROFILE_TYPE_ORG )
        self.main_org_profile.name = TEST_MAIN_ORG_NAME
        self.main_org_profile.save()

        for i in SUB_ORG_NAMES_LIST:
            sub_dep_profile = Profile( profile_type = PROFILE_TYPE_DEPARTAMENT )
            sub_dep_profile.name = i
            sub_dep_profile.save()
            r = Profile_Affiliation( main_profile=self.main_org_profile, sub_profile=sub_dep_profile )
            r.save()

    def test_Org_profile_type(self):
        self.assertEqual( self.main_org_profile.profile_type, PROFILE_TYPE_ORG )

    def test_Main_Org_Subs(self):
        self.assertEqual( self.main_org_profile.sub_profiles().count(), len( SUB_ORG_NAMES_LIST ) )

    def test_Main_Org_Subs_Name(self):
        for p in self.main_org_profile.sub_profiles():
            self.assertIn( p.sub_profile.name, SUB_ORG_NAMES_LIST )

    def test_Main_Org_Main(self):
        self.assertEqual( self.main_org_profile.main_profiles().count(), 0 )

    def test_Main_Org_Subs_Main(self):
        for p in self.main_org_profile.sub_profiles():
            sm = p.sub_profile.main_profiles()

            self.assertEqual( sm.count(), 1 )
            self.assertEqual( sm[0].main_profile, self.main_org_profile )

    def test_You_CANT_Link_Org_To_Self(self):
        r = Profile_Affiliation( main_profile=self.main_org_profile, sub_profile=self.main_org_profile )

        with self.assertRaises(Exception):
            r.save()

    def test_list_of_avail_for_affiliate(self):
        self.assertEqual( self.main_org_profile.list_of_avail_for_affiliate().count(), 0 )
