# wrapper for SVN

import svn.remote

REPO_BASE_URL = 'file:///d:/test/'
REPO_LOCAL_ROOT = ''

def Get_Info_For_Repo_Name( arg_repo_name ):
    r = svn.remote.RemoteClient( REPO_BASE_URL + arg_repo_name )
    return r.info()

# codes

VCS_CREATE_REPO_SUCCESS = 0
VCS_CREATE_REPO_FAIL_NOT_CONFIGURED = 1

# return (code, str)
def Create_New_Repo( ):
    #return ( VCS_CREATE_REPO_FAIL_NOT_CONFIGURED, 'file:///d:/test/repo' )
    return ( VCS_CREATE_REPO_SUCCESS, 'repo' )
    
def Get_List_For_Repo_Name( arg_repo_name ):
    r = svn.remote.RemoteClient( REPO_BASE_URL + arg_repo_name )
    return r.list()