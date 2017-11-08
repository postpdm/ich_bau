from project.repo_wrapper import *

from unittest import TestCase
import shutil, tempfile

class SVN_Wrapper_Abstract_Test(TestCase):
    def test_Get_Info(self):
        res = Get_Info_For_Repo_Name( 'some wrong repo' )
        self.assertEqual( res[0], VCS_REPO_FAIL_CALL )

    def test_Get_List(self):
        res = Get_List_For_Repo_Name( 'some wrong repo', 'some wrong path' )
        self.assertEqual( res[0], VCS_REPO_FAIL_CALL )

    def test_Repo_Conf_Name_Gen(self):
        repo_root = 'root_folder'
        repo_name = 'repo_name'
        t = Repo_File_Paths( repo_root, repo_name )

        self.assertEqual( t.svnserve_conf_full_name( ), repo_root + repo_name + '\\conf\\svnserve.conf' )
        self.assertEqual( t.pass_full_name( ),          repo_root + '\\passwd' ) # one passwd in root
        self.assertEqual( t.auth_full_name( ),          repo_root + repo_name + '\\conf\\authz' )

    def test_Repo_PW_Encoing(self):
        test_pw = 'some test pass'
        s = Gen_Repo_User_PW( test_pw )
        self.assertEqual( Decrypt_Repo_User_PW(s), test_pw )

    def test_VCS_Configured(self):
        self.assertEqual( VCS_Configured(), True )

class SVN_Wrapper_Temp_Dir_Test(TestCase):
    test_temp_dir = None

    def setUp(self):
        # Create a temporary directory
        self.test_temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_temp_dir)

    def test_Repo_Conf_In_Temp_Dir(self):
        repo_root = self.test_temp_dir
        repo_name = 'repo_name'
        t = Repo_File_Paths( repo_root, repo_name )

        Add_User_To_Main_PassFile( t.pass_full_name(), { 'user_name1' : 'pass', 'user_name2' : 'pass2' } )
        f = open( t.pass_full_name() )
        self.assertEqual(f.read(), '[users]\nuser_name1 = pass\nuser_name2 = pass2\n\n')