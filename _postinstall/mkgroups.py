from django.contrib.auth.models import Group, Permission
from django.shortcuts import get_object_or_404

from forum.models import Category, Thread, Post, Report


# The best resource on this is actually not the official docs, but this:
# http://tinyurl.com/django-groups

def get_perm(codename):
    return get_object_or_404(Permission, codename=codename)

moderators, created = Group.objects.get_or_create(name="Moderators")
if created:
    moderators.permissions = [
    # Category
        # get_perm('remove_category'),
        # get_perm('merge_category'),
    # Thread
        get_perm('remove_thread'),
        get_perm('moderate_thread'),
        # get_perm('merge_thread'),
        get_perm('sticky_thread'),
        get_perm('move_thread'),
        get_perm('lock_thread'),
    # Post
        get_perm('remove_post'),
        get_perm('moderate_post'),
    # User
        get_perm('tempban_user'),
        get_perm('permaban_user')
    ]
