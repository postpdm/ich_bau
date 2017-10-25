import os

DEBUG = False

MAIN_MESSAGE = 'Heroku demo. E-Mail if off. User upload flies is off. File repo is off'

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))

DATABASES = {
    "default": {
    }
}

import dj_database_url
# Change 'default' database configuration with $DATABASE_URL.
DATABASES['default'].update(dj_database_url.config(conn_max_age=500))

# SVN Repo settings
REPO_SVN = {
    "REPO_BASE_URL" : "",
    "REPO_LOCAL_ROOT" : "",

    "SVN_ADMIN_USER" : "",
    "SVN_ADMIN_PASSWORD" : "",

    "SVN_ADMIN_FULL_PATH" : "",
    "USERS_REPO_PW_KEY_SALT" : ""
}

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

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/site_media/static/"

# Make this unique, and don't share it with anybody.
SECRET_KEY = "drg10%o7jr3u%f!2_6*0y6ly$a7of#feycz@j6c!r!jyfpzx3g"

ALLOWED_HOSTS = [ '*' ]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "smtp.gmail.com"
# EMAIL_HOST_USER = "_@gmail.com"
# EMAIL_HOST_PASSWORD = '-'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True