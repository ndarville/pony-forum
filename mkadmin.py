#!/usr/bin/env python
from wsgi import *
from django.contrib.auth.models import User
# from forum.models import UserProfile
u, created = User.objects.get_or_create(username='admin')
if created:
    u.set_password('password')
    u.is_superuser = True
    u.is_staff = True
    u.save()