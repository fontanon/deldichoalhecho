.. contents::

===================
Development install
===================

1. Installing postgres (example databaseengine)
===============================================

::

    sudo aptitude update

    sudo apt-get install postgresql postgresql-contrib

    sudo su - postgres
    createuser --interactive
        Enter name of role to add: deldichoalhecho
        Shall the new role be a superuser? (y/n) y
    createdb --owner deldichoalhecho deldichoalhecho
    logout


2. Installing deldichoalhecho project
=====================================

Installing requirements

::

    sudo apt-get install git libpq-dev python-dev python-setuptools
    git clone https://github.com/goinnn/deldichoalhecho.git

    cd ~/deldichoalhecho
    sudo easy_install pip
    sudo pip install virtualenv

    virtualenv vdeldichoalhecho
    source vdeldichoalhecho/bin/activate
    pip install -r requirements.txt


Patching django-popolo

::
    cd vdeldichoalhecho/src/django-popolo/
    patch -p1 < ~/deldichoalhecho/patches/django-popolo.diff
    cd


::
    touch project_site/local_settings.py
    vim project_site/local_settings.py [Anex 3.1]

    sudo python manage.py makemigrations popolo
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py collectstatic
    python manage.py runserver (access via browser localhost:8000)

3. Annex
========

3.1 local_settings
==================

::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'deldichoalhecho',                           # Or path to database file if using sqlite3.
            'USER': 'deldichoalhecho',                           # Not used with sqlite3.
            'PASSWORD': '',                                      # Not used with sqlite3.
            'HOST': '',                                          # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                                          # Set to empty string for default. Not used with sqlite3.
        }
    }

