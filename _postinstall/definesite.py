#!/usr/bin/env python
"""
Saves the domain and name of your project as Site variables.
Capitalizes the first letter of the project name during this.
"""
try:
    import json
    with open('/home/dotcloud/environment.json') as f:
        from wsgi import *
        
        from django.contrib.sites.models import Site


        env = json.load(f)
        name = env['DOTCLOUD_PROJECT']

        s = Site.objects.get_current()
        s.domain = unicode(env['DOTCLOUD_WWW_HTTP_URL'])
        s.name   = unicode(name.capitalize())
        s.save()
except IOError:  # Development---not on DotCloud
    pass