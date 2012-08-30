import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'ponyforum.settings'
import sys
if not 'TRAVIS' in os.environ:
    sys.path.append('/home/dotcloud/current/ponyforum')
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()