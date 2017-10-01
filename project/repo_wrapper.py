# wrapper for SVN

import svn.remote
import svn.admin

import uuid

REPO_BASE_URL = 'file:///d:/test/repos/'
REPO_LOCAL_ROOT = "d:\\test\\repos\\"

SVN_ADMIN_FULL_PATH = 'd:\\test\\svn\\VisualSVN Server\\bin\\svnadmin.exe'

def Get_Info_For_Repo_Name( arg_repo_name ):
    r = svn.remote.RemoteClient( REPO_BASE_URL + arg_repo_name )
    return r.info()

# codes

VCS_CREATE_REPO_SUCCESS = 0
VCS_CREATE_REPO_FAIL_NOT_CONFIGURED = 1
VCS_CREATE_REPO_FAIL_CALL = 2

# return (code, str)
def Create_New_Repo( ):
    try:
        repo_guid_name = uuid.uuid4().hex
        a = svn.admin.Admin( svnadmin_filepath = SVN_ADMIN_FULL_PATH )
        a.create( REPO_LOCAL_ROOT + repo_guid_name, svnadmin_filepath = SVN_ADMIN_FULL_PATH )
        return ( VCS_CREATE_REPO_SUCCESS, repo_guid_name )
    except:
        return ( VCS_CREATE_REPO_FAIL_CALL, '' )
    
def Get_List_For_Repo_Name( arg_repo_name ):
    r = svn.remote.RemoteClient( REPO_BASE_URL + arg_repo_name )
    return r.list()