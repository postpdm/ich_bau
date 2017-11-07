from project.repo_wrapper import *

from unittest import TestCase

class SVN_Wrapper_Test(TestCase):
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