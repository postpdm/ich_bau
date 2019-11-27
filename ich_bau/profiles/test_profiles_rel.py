from django.contrib.auth.models import User, Permission
from .models import *

from django.test import TestCase, Client

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

# test view for profile affiliations

TEST_USER_NAME = 'USER'
TEST_USER_PW = 'USER_PW'

NEW_PEOPLE_PROFILE_NAME = 'NEW PEOPLE PROFILE NAME'
NEW_ORG_PROFILE_NAME = 'NEW ORG PROFILE NAME'

class Profile_Relation_Client_Test(TestCase):
    def setUp(self):
        if not User.objects.filter( username = TEST_USER_NAME ).exists():
            u = User.objects.create_user( username = TEST_USER_NAME, password = TEST_USER_PW )
            u.save()

    def test_profile_relation_view(self):
        self.assertEqual( Profile.objects.count(), 1 )
        self.assertEqual( Profile.objects.filter( profile_type__in = PROFILE_TYPE_FOR_TASK ).count(), 0 )

        c = Client()
        res = c.login(username=TEST_USER_NAME, password=TEST_USER_PW )

        self.assertTrue( res )

        response = c.post( reverse_lazy('profile_create'), { 'profile_type' : PROFILE_TYPE_PEOPLE, 'name' : NEW_PEOPLE_PROFILE_NAME,  } )
        self.assertEqual( response.status_code, 403 )
        self.assertEqual( Profile.objects.filter( profile_type__in = PROFILE_TYPE_FOR_TASK ).count(), 0 )
        
        # need to add the permissions
        add_project_permission = Permission.objects.get(codename='add_profile')
        test_user = User.objects.get( username = TEST_USER_NAME )
        test_user.user_permissions.add( add_project_permission )
        
        response = c.post( reverse_lazy('profile_create'), { 'profile_type' : PROFILE_TYPE_PEOPLE, 'name' : NEW_PEOPLE_PROFILE_NAME,  } )
        self.assertEqual( response.status_code, 302 )
        self.assertEqual( Profile.objects.filter( profile_type__in = PROFILE_TYPE_FOR_TASK ).count(), 1 )
        
        
        new_people = Profile.objects.get( name = NEW_PEOPLE_PROFILE_NAME )
        self.assertEqual( new_people.profile_type, PROFILE_TYPE_PEOPLE )

        response = c.post( reverse_lazy('profile_create'), { 'profile_type' : PROFILE_TYPE_ORG, 'name' : NEW_ORG_PROFILE_NAME,  } )
        self.assertEqual( response.status_code, 302 )
        self.assertEqual( Profile.objects.filter( profile_type__in = PROFILE_TYPE_FOR_TASK ).count(), 2 )

        new_org = Profile.objects.get( name = NEW_ORG_PROFILE_NAME )
        self.assertEqual( new_org.profile_type, PROFILE_TYPE_ORG )

        self.assertEqual( Profile_Affiliation.objects.count(), 0 )
        response = c.post( reverse_lazy('profile_add_sub', args = (new_org.id,) ), { 'sub_profile' : new_people.id, } )
        self.assertEqual( response.status_code, 302 )
        self.assertEqual( Profile_Affiliation.objects.count(), 1 )

        self.assertEqual( new_people.sub_profiles().count(), 0 )
        self.assertEqual( new_people.main_profiles().count(), 1 )
        self.assertEqual( new_org.sub_profiles().count(), 1 )
        self.assertEqual( new_org.main_profiles().count(), 0 )
