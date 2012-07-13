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
c, created = Category.objects.get_or_create(
        title_plain="Discussions", title_html="Discussions")

def mkuser(line):
    name = line.strip().lower().capitalize()
    u, created = User.objects.get_or_create(username=name)
    if created:
        # u.avatar = "..."
        u.set_password("password")  # Address security implications later
        u.save()

def author(line):
    mkuser(line)
    categories["AUTHOR"] = line.strip()

def translator(line):
    categories["TRANSLATOR"] = line.strip()

def title(line):
    categories["TITLE"] = line.strip()
    t, created = Thread.objects.get_or_create(
            title_plain=categories["TITLE"],
            title_html=sp(categories["TITLE"]),
            author=categories["AUTHOR"], category=c)
    if created:
        t.creation_date = now
        t.latest_reply_date =now
        t.save()

def characters(line):
    mkuser(line)
    characters[line.strip()] = u

def speaker(speaker, content):
    p, created = Post.objects.get_or_create(
            thread=t, author=characters[speaker],
            content_plain=content)
    if created:
        p.content_html = sd(md(content, extensions="nl2br"))
        p.creation_date = now
        p.save()

def parse_text(text):
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

        elif line.rstrip() in characters:
            speaker = line.rstrip()

        elif line == "\n":
            if speaker:
                speaker(speaker, content)
                speaker = ""
                content = ""
            else:
                category = ""

        elif category:
            if category == categories[0]:
                author(line)
            elif category == categories[1]:
                translator(line)
            elif category == categories[2]:
                title(line)
            elif category == categories[3]:
                characters(line, speaker)

        elif speaker:
            content += line.lstrip()

for root, dirs, files in os.walk(PATH):
    for name in files:
        if name == "text.txt":
            filepath = os.path.join(root, "text.txt")
            with open(filepath) as text:
                parse(text)