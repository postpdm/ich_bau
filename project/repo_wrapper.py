# wrapper for SVN

import svn.remote
import svn.admin

import uuid

from django.conf import settings

REPO_BASE_URL          = settings.REPO_SVN["REPO_BASE_URL"]
REPO_LOCAL_ROOT        = settings.REPO_SVN["REPO_LOCAL_ROOT"]

SVN_ADMIN_USER         = settings.REPO_SVN["SVN_ADMIN_USER"]
SVN_ADMIN_PASSWORD     = settings.REPO_SVN["SVN_ADMIN_PASSWORD"]

SVN_ADMIN_FULL_PATH    = settings.REPO_SVN["SVN_ADMIN_FULL_PATH"]

USERS_REPO_PW_KEY_SALT = settings.REPO_SVN["USERS_REPO_PW_KEY_SALT"]

# codes

VCS_REPO_SUCCESS = 0
VCS_REPO_FAIL_NOT_CONFIGURED = 1
VCS_REPO_FAIL_CALL = 2

# return True if yes
def VCS_Configured():
    if ( REPO_BASE_URL and REPO_LOCAL_ROOT and SVN_ADMIN_USER and SVN_ADMIN_PASSWORD and SVN_ADMIN_FULL_PATH and USERS_REPO_PW_KEY_SALT ):
        return True
    else:
        return False

#return (code,dict)
def Get_Info_For_Repo_Name( arg_repo_name, username=None, password=None, arg_echo = False ):
    if VCS_Configured():
        try:
            r = svn.remote.RemoteClient( REPO_BASE_URL + arg_repo_name, username, password )
            return ( VCS_REPO_SUCCESS, r.info() )
        except Exception as e:
            if arg_echo:
                print( e )
            return ( VCS_REPO_FAIL_CALL, None )
    else:
        return ( VCS_REPO_FAIL_NOT_CONFIGURED, None )

import configparser

def Write_Ini_for_CFG( arg_fn, arg_section_name, arg_dict ):
    config = configparser.ConfigParser()
    try:
        config.read_file(open( arg_fn ))
    except:
        pass

    if not ( arg_section_name in config.sections() ):
        config[ arg_section_name ] = {}

    for k,v in arg_dict.items():
        config[arg_section_name][k] = v

    with open(arg_fn, 'w') as configfile:
        config.write(configfile)

# const names
authz_fn  = 'authz'
passwd_fn = 'passwd'
svnserve_conf_fn = 'svnserve.conf'
conf_folder = 'conf'

class Repo_File_Paths():

    _repo_root_path = ''

    def __init__( self, arg_repo_root_path ):
        self._repo_root_path = arg_repo_root_path

    def auth_full_name( self ):
        return self._repo_root_path + '\\' + conf_folder + '\\' + authz_fn

    def pass_full_name( self ):
        return self._repo_root_path + '\\' + conf_folder + '\\' + passwd_fn

    def svnserve_conf_full_name( self ):
        return self._repo_root_path + '\\' + conf_folder + '\\' + svnserve_conf_fn

def Add_User_Info_to_Repo_CFG( arg_repo_file_paths, arg_user_and_pw_dict ): # arg_repo_file_paths - экземпляр Repo_File_Paths
    Write_Ini_for_CFG( arg_repo_file_paths.pass_full_name(), 'users', arg_user_and_pw_dict )
    Write_Ini_for_CFG( arg_repo_file_paths.auth_full_name(), '/', dict.fromkeys( arg_user_and_pw_dict.keys(), 'rw' ) )

def Write_Ini_For_New_Repo( arg_repo_root_path ):
    file_names = Repo_File_Paths( arg_repo_root_path )

    Write_Ini_for_CFG( file_names.svnserve_conf_full_name(), 'general', { 'anon-access' : 'none', 'auth-access' : 'write', 'password-db' : passwd_fn, 'authz-db' : authz_fn, } )
    Add_User_Info_to_Repo_CFG( file_names, { SVN_ADMIN_USER : SVN_ADMIN_PASSWORD } )

# return (code, str)
def Create_New_Repo( ):
    if VCS_Configured():
        try:
            repo_guid_name = uuid.uuid4().hex
            a = svn.admin.Admin( svnadmin_filepath = SVN_ADMIN_FULL_PATH )
            a.create( REPO_LOCAL_ROOT + repo_guid_name, svnadmin_filepath = SVN_ADMIN_FULL_PATH )
            Write_Ini_For_New_Repo( REPO_LOCAL_ROOT + repo_guid_name )
            return ( VCS_REPO_SUCCESS, repo_guid_name )
        except:
            return ( VCS_REPO_FAIL_CALL, '' )
    else:
        return ( VCS_REPO_FAIL_NOT_CONFIGURED, None )

from commons.simple_crypt import *
import base64

def Gen_Repo_User_PW( arg_test_pw = None ):
    if not( arg_test_pw is None ):
        pw = arg_test_pw
    else:
        pw = uuid.uuid4().hex
    pw = base64.b64encode( EnCrypt_Str(pw, USERS_REPO_PW_KEY_SALT ) ) # зашифровать и преобразовать в формат хранения
    return pw

def Decrypt_Repo_User_PW( arg_encrypted_pw ):
    return( DeCrypt_Str( base64.b64decode( arg_encrypted_pw ), USERS_REPO_PW_KEY_SALT ) ) # преобразовать их формата хранения и расшифровать

def Add_User_to_Repo( arg_repo_name, arg_user_and_pw_dict ):
    file_names = Repo_File_Paths( REPO_LOCAL_ROOT + arg_repo_name )
    Add_User_Info_to_Repo_CFG( file_names, arg_user_and_pw_dict )

# return (code, str)
def Get_List_For_Repo_Name( arg_repo_name, username=None, password=None, arg_echo = False ):
    if VCS_Configured():
        try:
            r = svn.remote.RemoteClient( REPO_BASE_URL + arg_repo_name, username, password )
            # list() is a lazy generator, it doesn't fetch data immediately. We need to convert it to real list to gain the connection error if exist
            return ( VCS_REPO_SUCCESS, list( r.list( extended = True ) ) )
        except Exception as e:
            if arg_echo:
                print( e )
            return ( VCS_REPO_FAIL_CALL, None )
    else:
        return ( VCS_REPO_FAIL_NOT_CONFIGURED, None )