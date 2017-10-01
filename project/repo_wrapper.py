# wrapper for SVN

import svn.remote

def Get_Info_For_Repo_URL( arg_repo_url ):
    r = svn.remote.RemoteClient( arg_repo_url )
    return r.info()
    
# codes

VCS_CREATE_REPO_SUCCESS = 0
VCS_CREATE_REPO_FAIL_NOT_CONFIGURED = 1

# return (code, str)
def Create_New_Repo( ):
    return ( VCS_CREATE_REPO_FAIL_NOT_CONFIGURED, 'file:///d:/test/repo' )
    #return ( VCS_CREATE_REPO_SUCCESS, 'file:///d:/test/repo' )