#!/usr/bin/env python
"""Creates placeholder objects."""
import datetime
import os
import random

if 'DOTCLOUD_ENVIRONMENT' in os.environ:
    import json
    from wsgi import *

    with open('/home/dotcloud/environment.json') as f:
        env = json.load(f)

from markdown import markdown as md
from smartypants import smartyPants as sp

from django.contrib.auth.models import User

from forum.models import Category, Thread, Post


PATH = os.path.join(os.curdir, "_postinstall", "placeholders")
categories, characters = {}, {}
PASSWORD = ''.join([random.SystemRandom().choice(
    'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(128)])
c, created = Category.objects.get_or_create(
        title_plain="Discussions", title_html="Discussions")

def mkuser(line):
    name = line.strip().lower().title()
    u, created = User.objects.get_or_create(username=name)
    if created:
        # u.avatar = "..."
        u.set_password(PASSWORD)
        u.save()
    return u

def mkauthor(line):
    global categories
    categories["AUTHOR"] = mkuser(line)

def mktranslator(line):
    global categories
    categories["TRANSLATOR"] = mkuser(line)

def mktitle(line):
    global categories
    global t
    categories["TITLE"] = line.strip()
    t, created = Thread.objects.get_or_create(
            title_plain=categories["TITLE"],
            title_html=sp(categories["TITLE"]),
            author=categories["AUTHOR"], category=c)

def mkcharacters(line):
    global characters
    characters[line.strip()] = mkuser(line)

def parse_speaker(speaker, content):
    speaker = speaker.lower().title()
    p, created = Post.objects.get_or_create(
            thread=t, author=characters[speaker],
            content_plain=content)
    if created:
        p.content_html = sp(md(text=content, extensions=["nl2br"]))
        p.creation_date = datetime.datetime.now()  # UTC?
        p.save()

def parse_manuscript(text):
    global categories
    global characters
    speaker, content, category, characters = "", "", "", {}
    categories = {
                    "AUTHOR": "",
                    "TRANSLATOR": "",
                    "TITLE": "",
                    "CHARACTERS": ""
                }

    for line in text:
        if line.rstrip() in categories:
            category = line.rstrip()

        elif line.rstrip().lower().title() in characters:
            speaker = line.rstrip()

        elif line == "\n":
            if speaker:
                parse_speaker(speaker, content)
                speaker, content = "", ""
            else:
                category = ""

        elif category:
            if category == "AUTHOR":
                mkauthor(line)
            elif category == "TRANSLATOR":
                mktranslator(line)
            elif category == "TITLE":
                mktitle(line)
#               "and" gets capitalized; fix
#               also: http://stackoverflow.com/a/1549644
            elif category == "CHARACTERS":
                mkcharacters(line)

        elif line.rstrip() == "END":
            pass

        elif speaker:
            content += line.lstrip()

for root, dirs, files in os.walk(PATH):
    for name in files:
        if name == "text.txt":
            filepath = os.path.join(root, "text.txt")
            with open(filepath) as text:
                parse_manuscript(text)
