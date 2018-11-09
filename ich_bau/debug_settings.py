import os

DEBUG = True

MAIN_MESSAGE = 'Debug mode'

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
#PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "dev.db",
    }
}

from .repo_settings_const import *

# SVN Repo settings
REPO_SVN = {
    "REPO_TYPE" : svn_serve,
    "REPO_BASE_URL" : "svn://localhost/",
    "REPO_LOCAL_ROOT" : "d:\\test\\repos\\",

    "SVN_ADMIN_USER" : "ich_bau_server",
    "SVN_ADMIN_PASSWORD" : "key",

    "SVN_ADMIN_FULL_PATH" : "d:\\test\\svn\\VisualSVN Server\\bin\\svnadmin.exe",
}

# REPO_SVN = {
    # "REPO_TYPE" : svn_apache,
    # "REPO_BASE_URL" : "http://localhost:8081/svn/",
    # "REPO_LOCAL_ROOT" : "d:\\p\\apache\\apachehouse\\Apache24\\Repositories\\",

    # "SVN_ADMIN_USER" : "ich_bau_server",
    # "SVN_ADMIN_PASSWORD" : "key",

    # "SVN_ADMIN_FULL_PATH" : "d:\\p\\apache\\apachehouse\\Apache24\\bin\\svnadmin.exe",
# }

# локальные адреса, разрешенные для отладки
INTERNAL_IPS = '127.0.0.1'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PACKAGE_ROOT, "site_media", "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = "/site_media/media/"

# Absolute path to the directory static files should be collected to.
# Don"t put anything in this directory yourself; store your static files
# in apps" "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PACKAGE_ROOT, "site_media", "static")
#STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/site_media/static/"
#STATIC_URL = "/static/"

# Make this unique, and don't share it with anybody.
SECRET_KEY = "plg10%o7jr3u%f!2_6*0y6ly$aiof#feycz@j6c!r!jyfpzx3x"

ALLOWED_HOSTS = [ '*' ]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "smtp.gmail.com"
# EMAIL_HOST_USER = "_@gmail.com"
# EMAIL_HOST_PASSWORD = '-'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True