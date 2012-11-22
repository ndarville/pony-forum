"""WSGI handler for dotCloud."""
import os
import sys

import django.core.handlers.wsgi


os.environ['DJANGO_SETTINGS_MODULE'] = 'ponyforum.settings'
sys.path.append('/home/dotcloud/current/ponyforum')
application = django.core.handlers.wsgi.WSGIHandler()
