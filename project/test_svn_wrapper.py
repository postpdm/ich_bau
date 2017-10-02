from project.repo_wrapper import *
  
from unittest import TestCase

class SVN_Wrapper_Test(TestCase):
    def test_Get_Info(self):
        res = Get_Info_For_Repo_Name( 'some wrong repo' )
        self.assertEqual( res[0], VCS_REPO_FAIL_CALL )

    def test_Get_List(self):
        res = Get_List_For_Repo_Name( 'some wrong repo' )
        self.assertEqual( res[0], VCS_REPO_FAIL_CALL )
