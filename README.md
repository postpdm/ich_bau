# Ich bau

Creation of simple task and project management system for Computer Aided Design and Drafting.

[![Django Support](https://img.shields.io/badge/Django-1.11-blue.svg)](https://github.com/postpdm/ich_bau)

[![Requirements Status](https://requires.io/github/postpdm/ich_bau/requirements.svg?branch=master)](https://requires.io/github/postpdm/ich_bau/requirements/?branch=master)

[![Coverage Status](https://coveralls.io/repos/github/postpdm/ich_bau/badge.svg?branch=master)](https://coveralls.io/github/postpdm/ich_bau?branch=master)

[![Build Status](https://travis-ci.org/postpdm/ich_bau.svg?branch=SVN_basic)](https://travis-ci.org/postpdm/ich_bau)

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
pip install -r requirements_dev.txt
manage.py test
manage.py migrate --run-syncdb
manage.py runserver
```
