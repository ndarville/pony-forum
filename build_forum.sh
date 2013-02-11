#!/bin/sh
#
# Builds an example forum with placeholder objects
# and an admin user with username 'admin', password 'password'.
#
# Requires that a postgreSQL database has been created for the forum.
set -e # stops execution on error
python manage.py syncdb --noinput
python manage.py schemamigration forum --initial
python manage.py migrate forum --fake
python _postinstall/mkadmin.py
python _postinstall/definesite.py
python _postinstall/mkplaceholders.py
python manage.py runserver
