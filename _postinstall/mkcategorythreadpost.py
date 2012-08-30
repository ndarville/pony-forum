#!/usr/bin/env python
"Creates a default category with a thread and post."

try:
    import json
    with open('/home/dotcloud/environment.json') as f:
        env = json.load(f)
    from wsgi import *
except IOError:  # Development---not on DotCloud
    pass

import datetime

from django.contrib.auth.models import User
from forum.models import Category, Thread, Post


c, created = Category.objects.get_or_create(pk=1)

if created:
    c.title_plain = "The Forum"
    c.title_html  = "The Forum"
    c.save()

    now  = datetime.datetime.now() # UTC?
    user = User.objects.get(pk=1)

    t = Thread(category=c, author=user,
               title_plain="Your First Thread",
               title_html="Your First Thread",
               creation_date=now, latest_reply_date=now)
    t.save()

    p = Post(thread=t, author=user,
             content_plain="Play around with the formatting and buttons.",
             content_html="<p>Play around with the formatting and buttons.</p>",
             creation_date=now)
    p.save()