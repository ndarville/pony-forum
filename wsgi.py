"""WSGI handler for dotCloud and default set-ups."""
import os
import sys


if 'DOTCLOUD_ENVIRONMENT' in os.environ:
    import django.core.handlers.wsgi

    os.environ['DJANGO_SETTINGS_MODULE'] = 'ponyforum.settings'
    sys.path.append('/home/dotcloud/current/ponyforum')
    application = django.core.handlers.wsgi.WSGIHandler()

elif 'TRAVIS' in os.environ:
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
