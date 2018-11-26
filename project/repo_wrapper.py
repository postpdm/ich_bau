# wrapper for SVN

import svn.remote
import svn.admin

import uuid

from django.conf import settings

import os

from ich_bau.repo_settings_const import *

# codes

VCS_REPO_SUCCESS = 0
VCS_REPO_FAIL_NOT_CONFIGURED = 1
VCS_REPO_FAIL_CALL = 2

# return True if yes
def VCS_Configured():
    # SVN_ADMIN_FULL_PATH could be empty (svnadmin is added in the env path) - do not check it
    if ( settings.REPO_SVN.get('REPO_TYPE') in KNOWN_REPO_TYPES ) and ( settings.REPO_SVN.get('REPO_BASE_URL') and settings.REPO_SVN.get('REPO_LOCAL_ROOT') and settings.REPO_SVN.get('SVN_ADMIN_USER') and settings.REPO_SVN.get('SVN_ADMIN_PASSWORD') ):
        return True
    else:
        return False

#return (code,dict)
def Get_Info_For_Repo_Name( arg_repo_name, username=None, password=None, arg_echo = False ):
    if VCS_Configured():
        try:
            r = svn.remote.RemoteClient( os.path.join( settings.REPO_SVN.get('REPO_BASE_URL'), arg_repo_name ), username, password )
            return ( VCS_REPO_SUCCESS, r.info() )
        except Exception as e:
            if arg_echo:
                print( e )
            return ( VCS_REPO_FAIL_CALL, None )
    else:
        return ( VCS_REPO_FAIL_NOT_CONFIGURED, None )

#return (code,dict)
# rev_num=None mean all
def Get_Log_For_Repo_Name( arg_repo_name, username=None, password=None, arg_echo = False, rev_num=None ):
    if VCS_Configured():
        try:
            r = svn.remote.RemoteClient( os.path.join( settings.REPO_SVN.get('REPO_BASE_URL' ), arg_repo_name ), username, password )
            # log() is a lazy generator, it doesn't fetch data immediately. We need to convert it to real list to gain the connection error if exist
            return ( VCS_REPO_SUCCESS, list( r.log_default(revision_from=rev_num, revision_to=rev_num, changelist=True) ) )

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

def Add_User_To_Main_PassFile( arg_pass_file, arg_dict ):
    if settings.REPO_SVN.get('REPO_TYPE') == svn_serve:
        section_name = 'users'
        delimiter = '='
    else:
        section_name = 'users' # for apache htpasswd it's ignored. Configparser can't write to root, so I just leave it here
        delimiter = ':'

    config = configparser.ConfigParser( delimiters = delimiter )
    try:
        config.read_file(open( arg_pass_file ))
    except:
        pass

    if not ( section_name in config.sections() ):
        config[ section_name ] = {}

    some_thing_to_write = False

    for k,v in arg_dict.items():
        if not config.has_option(section_name, k):
            config[section_name][k] = v
            some_thing_to_write = True

    if some_thing_to_write:
        with open(arg_pass_file, 'w') as configfile:
            config.write(configfile, space_around_delimiters = False)

# const names
authz_fn  = 'authz'
if settings.REPO_SVN.get('REPO_TYPE') == svn_serve:
    passwd_fn = 'passwd'
else:
    if settings.REPO_SVN.get('REPO_TYPE') == svn_apache:
        passwd_fn = 'htpasswd'

svnserve_conf_fn = 'svnserve.conf'
conf_folder_fn = 'conf'

two_folders_up = '../../'

class Repo_File_Paths():

    _repo_root_path = ''

    def __init__( self, arg_repo_root_path, arg_repo_name ):
        # trailing slash
        self._repo_root_path = os.path.join( arg_repo_root_path, '' )
        self._repo_path = os.path.join( self._repo_root_path + arg_repo_name, '' )

    def conf_folder(self):
        return os.path.join( self._repo_path + conf_folder_fn, '' )

    def auth_full_name( self ):
        return self.conf_folder() + authz_fn

    def pass_full_name( self ):
        # one passwd file for all repos
        return self._repo_root_path + passwd_fn

    def svnserve_conf_full_name( self ):
        return self.conf_folder() + svnserve_conf_fn

def Add_User_Info_to_Repo_CFG( arg_repo_file_paths, arg_user_and_pw_dict ): # arg_repo_file_paths - ύκηεμολÿπ Repo_File_Paths
    Add_User_To_Main_PassFile( arg_repo_file_paths.pass_full_name(), arg_user_and_pw_dict )
    Write_Ini_for_CFG( arg_repo_file_paths.auth_full_name(), '/', dict.fromkeys( arg_user_and_pw_dict.keys(), 'rw' ) )

def Write_Ini_For_New_Repo( arg_repo_root_path, arg_repo_name ):
    file_names = Repo_File_Paths( arg_repo_root_path, arg_repo_name )

    if settings.REPO_SVN.get('REPO_TYPE') == svn_serve:
        Write_Ini_for_CFG( file_names.svnserve_conf_full_name(), 'general', { 'anon-access' : 'none', 'auth-access' : 'write', 'password-db' : two_folders_up + passwd_fn, 'authz-db' : authz_fn, } )
    Add_User_Info_to_Repo_CFG( file_names, { settings.REPO_SVN.get('SVN_ADMIN_USER') : settings.REPO_SVN.get('SVN_ADMIN_PASSWORD') } )

# return (code, str)
def Create_New_Repo( ):
    if VCS_Configured():
        try:
            repo_guid_name = uuid.uuid4().hex
            if settings.REPO_SVN.get('SVN_ADMIN_FULL_PATH'):
                a = svn.admin.Admin( svnadmin_filepath = settings.REPO_SVN.get('SVN_ADMIN_FULL_PATH') )
            else:
                a = svn.admin.Admin()

            new_repo_name = settings.REPO_SVN.get('REPO_LOCAL_ROOT') + repo_guid_name
            a.create( new_repo_name )
            Write_Ini_For_New_Repo( settings.REPO_SVN.get('REPO_LOCAL_ROOT'), repo_guid_name )
            return ( VCS_REPO_SUCCESS, repo_guid_name )
        except:
            return ( VCS_REPO_FAIL_CALL, '' )
    else:
        return ( VCS_REPO_FAIL_NOT_CONFIGURED, None )

def Gen_Repo_User_PW( arg_test_pw = None ):
    if not( arg_test_pw is None ):
        pw = arg_test_pw
    else:
        pw = uuid.uuid4().hex

    return pw

def Add_User_to_Repo( arg_repo_name, arg_user_and_pw_dict ):
    file_names = Repo_File_Paths( REPO_LOCAL_ROOT, arg_repo_name )
    Add_User_Info_to_Repo_CFG( file_names, arg_user_and_pw_dict )

# return (code, str)
def Get_List_For_Repo_Name( arg_repo_name, arg_rel_path, username=None, password=None, arg_echo = False ):
    if VCS_Configured():
        try:
            r = svn.remote.RemoteClient( os.path.join( settings.REPO_SVN.get('REPO_BASE_URL'), arg_repo_name), username, password )
            # list() is a lazy generator, it doesn't fetch data immediately. We need to convert it to real list to gain the connection error if exist
            return ( VCS_REPO_SUCCESS, list( r.list( extended = True, rel_path = arg_rel_path ) ) )
        except Exception as e:
            if arg_echo:
                print( e )
            return ( VCS_REPO_FAIL_CALL, None )
    else:
        return ( VCS_REPO_FAIL_NOT_CONFIGURED, None )