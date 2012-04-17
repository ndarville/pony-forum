import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'ponyforum.settings'
import sys
sys.path.append('/home/dotcloud/current/ponyforum')
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()