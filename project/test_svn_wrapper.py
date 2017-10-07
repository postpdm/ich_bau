from project.repo_wrapper import *

from unittest import TestCase

class SVN_Wrapper_Test(TestCase):
    def test_Get_Info(self):
        res = Get_Info_For_Repo_Name( 'some wrong repo' )
        self.assertEqual( res[0], VCS_REPO_FAIL_CALL )

    def test_Get_List(self):
        res = Get_List_For_Repo_Name( 'some wrong repo' )
        self.assertEqual( res[0], VCS_REPO_FAIL_CALL )

    def test_Repo_Conf_Name_Gen(self):
        s = ''
        t = Repo_File_Paths( s )

        self.assertEqual( t.svnserve_conf_full_name( ), s + '\\conf\\svnserve.conf' )
        self.assertEqual( t.pass_full_name( ),          s + '\\conf\\passwd' )
        self.assertEqual( t.auth_full_name( ),          s + '\\conf\\authz' )