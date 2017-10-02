# wrapper for SVN

import svn.remote
import svn.admin

import uuid

REPO_BASE_URL = 'file:///d:/test/repos/'
REPO_LOCAL_ROOT = "d:\\test\\repos\\"

SVN_ADMIN_FULL_PATH = 'd:\\test\\svn\\VisualSVN Server\\bin\\svnadmin.exe'

# codes

VCS_REPO_SUCCESS = 0
VCS_REPO_FAIL_NOT_CONFIGURED = 1
VCS_REPO_FAIL_CALL = 2

#return (code,dict)
def Get_Info_For_Repo_Name( arg_repo_name, arg_echo = False ):
    if ( REPO_BASE_URL is None ) or ( REPO_BASE_URL == '' ):
        return ( VCS_REPO_FAIL_NOT_CONFIGURED, None )
    else:    
        try:
            r = svn.remote.RemoteClient( REPO_BASE_URL + arg_repo_name )
            return ( VCS_REPO_SUCCESS, r.info() )
        except Exception as e:
            if arg_echo:
                print( e )
            return ( VCS_REPO_FAIL_CALL, None )

# return (code, str)
def Create_New_Repo( ):
    if ( REPO_BASE_URL is None ) or ( REPO_BASE_URL == '' ):
        return ( VCS_REPO_FAIL_NOT_CONFIGURED, None )
    else:
        try:
            repo_guid_name = uuid.uuid4().hex
            a = svn.admin.Admin( svnadmin_filepath = SVN_ADMIN_FULL_PATH )
            a.create( REPO_LOCAL_ROOT + repo_guid_name, svnadmin_filepath = SVN_ADMIN_FULL_PATH )
            return ( VCS_REPO_SUCCESS, repo_guid_name )
        except:
            return ( VCS_REPO_FAIL_CALL, '' )
    
# return (code, str)
def Get_List_For_Repo_Name( arg_repo_name ):
    if ( REPO_BASE_URL is None ) or ( REPO_BASE_URL == '' ):
        return ( VCS_REPO_FAIL_NOT_CONFIGURED, None )
    else:    
        try:
            r = svn.remote.RemoteClient( REPO_BASE_URL + arg_repo_name )
            # list() is a lazy generator, it doesn't fetch data immediately. We need to convert it to real list to gain the connection error if exist
            return ( VCS_REPO_SUCCESS, list( r.list() ) )
        except Exception as e:
            print( e )
            return ( VCS_REPO_FAIL_CALL, None )