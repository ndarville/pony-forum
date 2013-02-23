#!/usr/bin/env python
"""Saves the domain and name of your project as Site variables.
Capitalizes the first letter of the project name during this.
"""
import os

from django.conf import settings as project_settings
from django.contrib.sites.models import Site


if 'DOTCLOUD_ENVIRONMENT' in os.environ:
    import json
    from wsgi import *

    with open('/home/dotcloud/environment.json') as f:
        env = json.load(f)
        name = env['DOTCLOUD_PROJECT']

        s = Site.objects.get_current()
        s.domain = unicode(env['DOTCLOUD_WWW_HTTP_URL'])
        s.name   = unicode(name.capitalize())
        s.save()

elif project_settings.LOCAL_DEVELOPMENT:
    s = Site.objects.get_current()
    s.domain = "127.0.0.1:8000"
    s.name   = "The Forum"
    s.save()
