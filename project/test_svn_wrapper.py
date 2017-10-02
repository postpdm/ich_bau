from .repo_wrapper import *
  
from unittest import TestCase

class SVN_Wrapper_Test(TestCase):
    def test_Something(self):        
        res = Get_Info_For_Repo_Name( 'some wrong repo' )
        self.assertEqual( res[0], VCS_REPO_FAIL_CALL )        