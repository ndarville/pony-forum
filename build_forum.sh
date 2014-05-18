#!/bin/sh
#
# Builds an example forum with placeholder objects
# and an admin user with username 'admin', password 'password'.
#
# Requires that a postgreSQL database has been created for the forum.
#
# If you have used Pony Forum before, make sure that there is no
# forum/migrations/ folder, since that will break this script.
set -e # stops execution on error
rm -rf forum/migrations
python manage.py schemamigration forum --initial
python manage.py syncdb --noinput
python manage.py migrate forum
python _postinstall/mkadmin.py
python _postinstall/definesite.py
python _postinstall/mkplaceholders.py
python -Wall manage.py test forum
