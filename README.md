# Ich bau

Creation of simple task and project management system for Computer Aided Design and Drafting.

[![Django Support](https://img.shields.io/badge/Django-2.05-blue.svg)](https://github.com/postpdm/ich_bau)

[![Requirements Status](https://requires.io/github/postpdm/ich_bau/requirements.svg?branch=master)](https://requires.io/github/postpdm/ich_bau/requirements/?branch=master)

[![Coverage Status](https://coveralls.io/repos/github/postpdm/ich_bau/badge.svg?branch=master)](https://coveralls.io/github/postpdm/ich_bau?branch=master)

[![Build Status](https://travis-ci.org/postpdm/ich_bau.svg?branch=SVN_basic)](https://travis-ci.org/postpdm/ich_bau)



[![](https://img.shields.io/github/issues-pr/postpdm/ich_bau.svg)](https://github.com/postpdm/ich_bau/pulls)
[![](https://img.shields.io/github/issues-pr-closed/postpdm/ich_bau.svg)](https://github.com/postpdm/ich_bau/pulls?q=is%3Apr+is%3Aclosed)



## Main goals

* Simple but usefull planning and task flow
* Small group collaboration
* Impressive power with CAD file handling, vector files and output documents
* Practically valuable subset of PLM and CRM functions

## Install

You need the actual Python 3.6 version.

For testing

```
virtualenv.exe ich_bau_test
git clone https://github.com/postpdm/ich_bau.git
activate
pip install -r requirements.txt
manage.py test
manage.py migrate --run-syncdb
manage.py createsuperuser
manage.py runserver
```

### Settings

| Setting name | Sample                 |               Description               |
|--------------|------------------------|:---------------------------------------:|
| MAIN_MESSAGE | Debug mode ON          | Some test massage as alert at each page |
| DATABASES    | Database configuration | Standard Django configuration. `dj_database_url` is supported |
| REPO_SVN     | SVN file repo          |                                         |

For your instance, please create `production_settings.py` in `ich_bau` folder.

### Customization

For template customization - use `templates` folder in the root of the project. HTML files in this folder will ignored by `.gitignore` file, so your custom templates will not be committed to project repo.

For sample - place `homepage.html` in `templates` folder of your site to overwrite the start page.

### Testing file repo functions

For testing file repo functions you need actual version of Apache Subversion client and server.

* `svn` and `svnadmin` command-line clients in your PATH
* setting up the `REPO_SVN` settingns in `settings.py`
* `file://`, `svn://`, `http://` or `https://` connections is available to your repos 

### Permissions

New project could be created by super user or by user with `project.add_project` permission (assign it in Admin panel).

