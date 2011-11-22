import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'hellodjango.settings'
import sys
sys.path.append('/home/dotcloud/current/hellodjango')
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
