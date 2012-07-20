#!/usr/bin/env python
"Creates placeholder objects."

from wsgi import *

import datetime
import os

from django.contrib.auth.models import User
from forum.models import Category, Thread, Post

from markdown import markdown as md
from smartypants import smartyPants as sp


PATH = os.path.join(os.curdir, "_postinstall", "placeholders")
now = datetime.datetime.now()  # UTC?
categories, characters = {}, {}
c, created = Category.objects.get_or_create(
        title_plain="Discussions", title_html="Discussions")

def mkuser(line):
    name = line.strip().lower().capitalize()
    u, created = User.objects.get_or_create(username=name)
    if created:
        # u.avatar = "..."
        u.set_password("password")  # Address security implications later
        u.save()
    return u

def author(line):
    global categories
    categories["AUTHOR"] = mkuser(line)

def translator(line):
    global categories
    categories["TRANSLATOR"] = mkuser(line)

def title(line):
    global categories
    categories["TITLE"] = line.strip()
    t, created = Thread.objects.get_or_create(
            title_plain=categories["TITLE"],
            title_html=sp(categories["TITLE"]),
            author=categories["AUTHOR"], category=c)

def characters(line):
    global characters
    characters[line.strip()] = mkuser(line)

def parse_speaker(speaker, content):
    global characters
    p, created = Post.objects.get_or_create(
            thread=t, author=characters[speaker],
            content_plain=content)
    if created:
        p.content_html = sd(md(content, extensions="nl2br"))
        p.creation_date = now
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
                author(line)
            elif category == "TRANSLATOR":
                translator(line)
            elif category == "TITLE":
                title(line)
#               "and" gets capitalized; fix
#               also: http://stackoverflow.com/a/1549644
            elif category == "CHARACTERS":
                characters(line, speaker)

        elif speaker:
            content += line.lstrip()

for root, dirs, files in os.walk(PATH):
    for name in files:
        if name == "text.txt":
            filepath = os.path.join(root, "text.txt")
            with open(filepath) as text:
                parse_manuscript(text)