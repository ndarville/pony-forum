"""WSGI handler for dotCloud and default set-ups."""
import os

if 'DOTCLOUD_ENVIRONMENT' in os.environ:
    import sys
    import django.core.handlers.wsgi

    os.environ['DJANGO_SETTINGS_MODULE'] = 'ponyforum.settings'
    sys.path.append('/home/dotcloud/current/ponyforum')
    application = django.core.handlers.wsgi.WSGIHandler()

else:
    from django.core.wsgi import get_wsgi_application

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ponyforum.settings")
    application = get_wsgi_application()
