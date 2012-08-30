#!/usr/bin/env python

try:
    import json
    with open('/home/dotcloud/environment.json') as f:
        env = json.load(f)
    from wsgi import *
except IOError:  # Development---not on DotCloud
    pass

from django.contrib.auth.models import User


u, created = User.objects.get_or_create(username='admin')
if created:
    u.set_password('password')
    u.is_superuser = True
    u.is_staff = True
    u.save()