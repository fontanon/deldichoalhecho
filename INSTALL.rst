.. contents::

=======
Install
=======

1. Installing postgres(example databaseengine)
==============================================

::

    sudo aptitude update

    sudo apt-get install postgresql postgresql-contrib

    sudo su - postgres
    createuser --interactive
        Enter name of role to add: deldichoalhecho
        Shall the new role be a superuser? (y/n) y
    createdb --owner deldichoalhecho deldichoalhecho
    logout


2. Creating a local user
========================

::

    sudo groupadd --system deldichoalhecho
    sudo useradd --system --gid deldichoalhecho --shell /bin/bash --home /home/deldichoalhecho deldichoalhecho
    sudo mkdir /home/deldichoalhecho
    sudo adduser deldichoalhecho sudo
    passwd deldichoalhecho
    Enter new UNIX password: ***************
    Retype new UNIX password: **************
    sudo su - deldichoalhecho
    sudo chown deldichoalhecho:deldichoalhecho . 


3. Installing deldichoalhecho project
=====================================


Installing requirements

::

    sudo apt-get install git libpq-dev python-dev python-setuptools
    git clone https://github.com/goinnn/deldichoalhecho.git

    cd ~/deldichoalhecho
    sudo easy_install pip
    sudo pip install -r requirements.txt

Patching django-popolo

::

    cd /home/deldichoalhecho/deldichoalhecho/src/django-popolo
    patch -p1 < /home/deldichoalhecho/deldichoalhecho/patches/django-popolo.diff
    cd /home/deldichoalhecho/deldichoalhecho


::

    touch project_site/local_settings.py
    vim project_site/local_settings.py [Anex 7.1]

    sudo python manage.py makemigrations popolo
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py collectstatic


4. Installing Gunicorn (wsgi server)
====================================

::

    sudo pip install gunicorn setproctitle
    cd ~/deldichoalhecho
    gunicorn project_site.wsgi:application --bind 188.166.14.177:8001 (check works via http, browser)
    cd ..
    mkdir bin
    cd bin
    vim gunicorn_start [Annex 7.2]
    sudo chmod u+x gunicorn_start


5. Installing Supervisor (process manager)
==========================================

::

    sudo apt-get install supervisor
    sudo vim /etc/supervisor/conf.d/deldichoalhecho.conf [Annex 7.3]
    mkdir /home/deldichoalhecho/logs
    touch /home/deldichoalhecho/logs/gunicorn_supervisor.log
    sudo supervisorctl reread
    sudo /etc/init.d/supervisor restart
    sudo supervisorctl status deldichoalhecho (check)


6. Nginx (http server)
======================

::

    sudo apt-get install nginx
    sudo service apache2 stop
    sudo service nginx start (check via web)
    sudo vim /etc/nginx/sites-available/deldichoalhecho [Annex 7.4]
    sudo ln -s /etc/nginx/sites-available/deldichoalhecho /etc/nginx/sites-enabled/deldichoalhecho
    sudo service nginx restart


7. Annex
========

7.1 local_settings
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

7.2 Annex gunicorn_start script
===============================

::

    #!/bin/bash

    NAME="deldichoalhecho"                                                      # Name of the application
    DJANGODIR=/home/deldichoalhecho/deldichoalhecho/                            # Django project directory
    SOCKFILE=/home/deldichoalhecho/deldichoalhecho/run/gunicorn.sock            # we will communicte using this unix socket
    USER=deldichoalhecho                                                        # the user to run as
    GROUP=deldichoalhecho                                                       # the group to run as
    NUM_WORKERS=3                                                               # how many worker processes should Gunicorn spawn
    DJANGO_SETTINGS_MODULE=project_site.settings                                # which settings file should Django use
    DJANGO_WSGI_MODULE=project_site.wsgi                                        # WSGI module name

    echo "Starting $NAME as `whoami`"

    cd $DJANGODIR
    export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
    export PYTHONPATH=$DJANGODIR:$PYTHONPATH

    # Create the run directory if it doesn't exist
    RUNDIR=$(dirname $SOCKFILE)
    test -d $RUNDIR || mkdir -p $RUNDIR

    # Start your Django Unicorn
    # Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
    exec gunicorn ${DJANGO_WSGI_MODULE}:application \
    --name $NAME \
    --workers $NUM_WORKERS \
    --user=$USER --group=$GROUP \
    --bind=unix:$SOCKFILE \
    --log-level=debug \
    --log-file=-

7.2 Annex deldichoalhecho.conf supervisor configuration
=======================================================

::

    [program:deldichoalhecho]
    command = /home/deldichoalhecho/bin/gunicorn_start                    ; Command to start app
    user = deldichoalhecho                                                ; User to run as
    stdout_logfile = /home/deldichoalhecho/logs/gunicorn_supervisor.log   ; Where to write log messages
    redirect_stderr = true                                                ; Save stderr in the same log
    environment=LANG=en_US.UTF-8,LC_ALL=en_US.UTF-8


7.4 Annex deldichoalhecho nginx configuration
=============================================

::

    upstream deldichoalhecho_app_server {
    # fail_timeout=0 means we always retry an upstream even if it failed
    # to return a good HTTP response (in case the Unicorn master nukes a
    # single worker for timing out).

    server unix:/home/deldichoalhecho/deldichoalhecho/run/gunicorn.sock fail_timeout=0;
    }

    server {

        listen   80;
        server_name *.fontanon.org;

        client_max_body_size 4G;

        access_log /home/deldichoalhecho/logs/nginx-access.log;
        error_log /home/deldichoalhecho/logs/nginx-error.log;

        location /static/ {
            alias   /home/deldichoalhecho/deldichoalhecho/staticfiles/;
        }

        location /media/ {
            alias   /home/deldichoalhecho/deldichoalhecho/mediafiles/;
        }

        location / {
            # an HTTP header important enough to have its own Wikipedia entry:
            #   http://en.wikipedia.org/wiki/X-Forwarded-For
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

            # enable this if and only if you use HTTPS, this helps Rack
            # set the proper protocol for doing redirects:
            # proxy_set_header X-Forwarded-Proto https;

            # pass the Host: header from the client right along so redirects
            # can be set properly within the Rack application
            proxy_set_header Host $http_host;

            # we don't want nginx trying to do something clever with
            # redirects, we set the Host: header above already.
            proxy_redirect off;

            # set "proxy_buffering off" *only* for Rainbows! when doing
            # Comet/long-poll stuff.  It's also safe to set if you're
            # using only serving fast clients with Unicorn + nginx.
            # Otherwise you _want_ nginx to buffer responses to slow
            # clients, really.
            # proxy_buffering off;

            # Try to serve static files from nginx, no point in making an
            # *application* server like Unicorn/Rainbows! serve static files.
            if (!-f $request_filename) {
                proxy_pass http://deldichoalhecho;
                break;
            }
        }
    }

