from project.repo_wrapper import *

import pathlib

def get_TEST_REPO_SVN_FILE( arg_path ):
    return {
    "REPO_TYPE" : svn_file,
    "REPO_BASE_URL" : pathlib.Path( arg_path ).as_uri(),
    "REPO_LOCAL_ROOT" : arg_path,

    "SVN_ADMIN_USER" : "test_svn_admin",
    "SVN_ADMIN_PASSWORD" : "test_key",

    "SVN_ADMIN_FULL_PATH" : None, 
    }