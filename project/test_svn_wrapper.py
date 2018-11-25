from project.repo_wrapper import *

from unittest import TestCase
from django.test.testcases import SimpleTestCase
import shutil, tempfile
import svn.remote
import svn.admin

import os
import pathlib


class SVN_Wrapper_Abstract_Test(TestCase):
    def test_Get_Info(self):
        res = Get_Info_For_Repo_Name( 'some wrong repo' )
        self.assertEqual( res[0], VCS_REPO_FAIL_CALL )

    def test_Get_Log(self):
        res = Get_Log_For_Repo_Name( 'some wrong repo' )
        self.assertEqual( res[0], VCS_REPO_FAIL_CALL )

    def test_Get_List(self):
        res = Get_List_For_Repo_Name( 'some wrong repo', 'some wrong path' )
        self.assertEqual( res[0], VCS_REPO_FAIL_CALL )

    def test_Repo_Conf_Name_Gen(self):
        repo_root = 'root_folder'
        repo_name = 'repo_name'
        t = Repo_File_Paths( repo_root, repo_name )

        self.assertEqual( t.conf_folder( ),             os.path.join( repo_root, repo_name, 'conf', '' ) )
        self.assertEqual( t.svnserve_conf_full_name( ), os.path.join( repo_root, repo_name, 'conf', 'svnserve.conf' ) )
        if settings.REPO_SVN.get('REPO_TYPE') == svn_serve:
            self.assertEqual( t.pass_full_name( ),      os.path.join( repo_root, 'passwd' ) ) # one passwd in root
        else:
            if settings.REPO_SVN.get('REPO_TYPE') == svn_apache:
                self.assertEqual( t.pass_full_name( ),  os.path.join( repo_root, 'htpasswd' ) ) # one passwd in root

        self.assertEqual( t.auth_full_name( ),          os.path.join( repo_root, repo_name, 'conf', 'authz' ) )

    def test_Gen_Repo_User_PW(self):
        pw= Gen_Repo_User_PW()
        self.assertNotEqual( pw, '')

    def test_VCS_Configured(self):
        self.assertEqual( VCS_Configured(), True )

class SVN_Wrapper_Temp_Dir_Test(TestCase):
    test_temp_dir = None

    def setUp(self):
        # Create a temporary directory
        if not self.test_temp_dir:
            self.test_temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        if self.test_temp_dir:
            shutil.rmtree(self.test_temp_dir, True )
            self.test_temp_dir = None

    def test_Repo_Users_In_Temp_Dir(self):
        repo_root = self.test_temp_dir
        repo_name = 'repo_name'
        t = Repo_File_Paths( repo_root, repo_name )
        fn = t.pass_full_name()

        Add_User_To_Main_PassFile( fn, { 'user_name1' : 'pass', 'user_name2' : 'pass2' } )
        f = open( fn )

        if settings.REPO_SVN.get('REPO_TYPE') == svn_serve:
            self.assertEqual(f.read(), '[users]\nuser_name1=pass\nuser_name2=pass2\n\n')
        else:
            if settings.REPO_SVN.get('REPO_TYPE') == svn_apache:
                self.assertEqual(f.read(), '[users]\nuser_name1:pass\nuser_name2:pass2\n\n')
        f.close()

    def test_Repo_Conf_In_Temp_Dir(self):
        repo_root = self.test_temp_dir
        repo_name = 'repo_name'
        t = Repo_File_Paths( repo_root, repo_name )
        fn = t.svnserve_conf_full_name()

        import os
        os.makedirs( t.conf_folder() ) # force path to cfg

        Write_Ini_for_CFG( fn, 'some_section', { 'option' : 'value' } )
        f = open( fn )
        self.assertEqual(f.read(), '[some_section]\noption = value\n\n')
        f.close()

    def test_SVN_Client(self):
        path = self.test_temp_dir + '/test_repo_name'
        self.assertFalse(os.path.exists( path ))
        a = svn.admin.Admin( )
        a.create( path )
        self.assertTrue(os.path.exists( path ))

        self.assertTrue(os.path.exists( path + '/conf' ))
        self.assertTrue(os.path.isfile( path + '/conf/authz' ))

        f = open( path + '/conf/authz' )

        self.assertIn( '[groups]', f.read() )
        f.close()

        # convert file path to file:// url
        file_path_ulr = pathlib.Path(path).as_uri()
        r = svn.remote.RemoteClient( file_path_ulr, 'u', 'p' )

        self.assertEqual( file_path_ulr, r.info()['url'] )
        self.assertEqual( '^/', r.info()['relative_url'] )


class SVN_Wrapper_Overwrite_Settings(SimpleTestCase):
    def test_Overwrite_Settings_None(self):
        with self.settings( REPO_SVN = {} ):
            self.assertTrue( settings.REPO_SVN.get('REPO_TYPE') == None )
            self.assertFalse( VCS_Configured() )
            self.assertTrue( Get_Info_For_Repo_Name( 'meaningless name' )[0] == VCS_REPO_FAIL_NOT_CONFIGURED )
            self.assertTrue( Get_Log_For_Repo_Name( 'meaningless name' )[0] == VCS_REPO_FAIL_NOT_CONFIGURED )
            self.assertTrue( Get_List_For_Repo_Name( 'meaningless name', 'meaningless path' )[0] == VCS_REPO_FAIL_NOT_CONFIGURED )

    def test_Overwrite_Settings_File_Protocol(self):
        path =  tempfile.gettempdir()
        with self.settings( REPO_SVN = {
            "REPO_TYPE" : svn_file,
            "REPO_BASE_URL" : pathlib.Path( path ).as_uri(),
            "REPO_LOCAL_ROOT" : path,

            "SVN_ADMIN_USER" : "svn_admin",
            "SVN_ADMIN_PASSWORD" : "key",

            "SVN_ADMIN_FULL_PATH" : "", } ):

            self.assertTrue( settings.REPO_SVN.get('REPO_TYPE') == svn_file )
            self.assertTrue( settings.REPO_SVN.get('REPO_LOCAL_ROOT') == path )

class SVN_Wrapper_Client_Test(SimpleTestCase):
    test_temp_dir = None

    def setUp(self):
        # Create a temporary directory
        if not self.test_temp_dir:
            self.test_temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        if self.test_temp_dir:
            shutil.rmtree(self.test_temp_dir, True )
            self.test_temp_dir = None

    def test_SVN_Wrapper(self):
        path = os.path.join(self.test_temp_dir, '' )
        with self.settings( REPO_SVN = {
            "REPO_TYPE" : svn_file,
            "REPO_BASE_URL" : pathlib.Path( path ).as_uri(),
            "REPO_LOCAL_ROOT" : path,

            "SVN_ADMIN_USER" : "test_svn_admin",
            "SVN_ADMIN_PASSWORD" : "test_key",

            "SVN_ADMIN_FULL_PATH" : None, } ):

            repo = Create_New_Repo()
            self.assertTrue( repo[0] == 0 )
            self.assertTrue(os.path.exists( os.path.join( path , repo[1] ) ) )
