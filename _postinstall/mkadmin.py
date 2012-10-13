#!/usr/bin/env python
import os

if 'DOTCLOUD_ENVIRONMENT' in os.environ:
    import json
    from wsgi import *

    with open('/home/dotcloud/environment.json') as f:
        env = json.load(f)

from django.contrib.auth.models import User


u, created = User.objects.get_or_create(username='admin')
if created:
    u.set_password('password')
    u.is_superuser = True
    u.is_staff = True
    u.save()