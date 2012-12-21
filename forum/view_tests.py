"""Tests the views in views.py by passing their functions test arguments."""
import json
import os

from django.core.urlresolvers import reverse
from django.test.client       import Client

from django_nose              import FastFixtureTestCase as TestCase

from forum.models             import Category, Thread, Post, Report


test_text = "Howdy ho."

# Determines count of thread and post objects
# and ID of test category, threads, and post
with open('forum/fixtures/forum_example.json') as f:
    test_thread_count, test_post_count = 0, 0

    for x in json.load(f):
        if x['model'] == 'forum.category':
            test_category_id = x['pk']
        elif x['model'] == 'forum.thread':
            test_thread_count += 1
            if x['fields']['title_plain'] == 'Merge Thread 1':
                merge_thread_1_id = x['pk']
            elif x['fields']['title_plain'] == 'Merge Thread 2':
                merge_thread_2_id = x['pk']
        elif x['model'] == 'forum.post':
            test_post_count += 1
            if x['fields']['content_plain'].startswith('Test post'):
                test_post_id = x['pk']
                test_thread_id = x['fields']['thread']
                test_user_id = x['fields']['author']


def logIn(username='admin', password='password'):
    """Log in a user on a test client."""
    client = Client()
    client.login(username=username, password=password)

    return client


class LoginTest(TestCase):
    """Tests user log-in."""
    fixtures = ['admin_user.json']

    def setUp(self):
        self.client = Client()

    def test_login(self):
        """Log in an admin user.

        Success criterion: 200 response, including redirects.
        """
        self.assertEqual(
            self.client.post(
                reverse('login', args=()),
                {'username': 'admin', 'password': 'password'},
                follow=True
            ).status_code,
            200)


class CategoryTests(TestCase):
    """Tests operations with category objects."""
    fixtures = ['admin_user.json', 'forum_example.json']

    def test_get(self):
        """Tests the display of a category object."""
        self.client.get(
            reverse('forum.views.category',
            args=(test_category_id,)))

    def test_add(self):
        self.client = logIn()
        self.client.post(
            reverse('forum.views.add', args=()),
            {'title': test_text})


class ThreadTests(TestCase):
    """Tests operations with thread objects."""
    fixtures = ['forum_example.json']

    def setUp(self):
        self.client = logIn()

    def test_get(self):
        """Tests the display of a thread object."""
        self.client.get(reverse('forum.views.thread', args=(test_thread_id,)))

    def test_show_posts_by_author(self):
        """Tests the display of posts by a specific user in a thread."""
        self.client.get(
            reverse('forum.views.thread',
            args=(test_category_id, test_user_id,)))

    def test_create(self):
        """Tests creation of thread object."""
        self.client.post(
            reverse('forum.views.create', args=(test_category_id,)),
            {'title': test_text, 'content': test_text})

    def test_lock(self):
        """Tests locking of thread object."""
        self.client.post(
            reverse('forum.views.lock_thread', args=(test_thread_id,)),
            {'lock': 'Lock'})

 #! TODO
 #  def test_unlock

    def test_merge(self):
        """Tests locking of thread object."""
        self.client.post(
            reverse('forum.views.merge_thread', args=(merge_thread_1_id,)),
            {'other-thread-id':   merge_thread_2_id,
             'new-thread-title': 'Merge Thread 3'})

    def test_moderate(self):
        """Tests moderation of thread object."""
        self.client.post(
            reverse('forum.views.moderate_thread', args=(test_thread_id,)),
            {'lock' : 'Lock',
             'title':  test_text})

    def test_remove(self):
        """Tests removal of a thread object."""
        self.client.post(
            reverse(
                'forum.views.remove',
                kwargs={'object_id': test_thread_id, 'object_type': 'thread'}),
            {'remove': 'Remove'})

 #! TODO
 #  def test_restore

    def test_sticky(self):
        """Tests stickification of thread object."""
        self.client.post(
            reverse('forum.views.sticky_thread', args=(test_thread_id,)),
            {'sticky' : 'Sticky'})

 #! TODO
 #  def test_unsticky


class PostTests(TestCase):
    """Test operations with post objects."""
    fixtures = ['forum_example.json']

    def setUp(self):
        self.client = logIn()

    def test_get(self):
        """Tests the display of a post object."""
        self.client.get(reverse('forum.views.post', args=(test_post_id,)))

    def test_reply(self):
        """Tests creation of a post object."""
        self.client.post(
            reverse('forum.views.reply', args=(test_thread_id,)),
            {'content': test_text})

    def test_edit(self):
        """Tests editing of a post object."""
        self.client.post(
            reverse('forum.views.edit', args=(test_post_id,)),
            {'content': test_text})

    def test_remove(self):
        """Tests removal of a post object."""
        self.client.post(
            reverse(
                'forum.views.remove',
                kwargs={'object_id': test_post_id, 'object_type': 'post'}),
            {'remove': 'Remove'})


class SiteConfigurationTests(TestCase):
    """Test operations related to the site configuration view."""
    fixtures = ['admin_user.json']

    def setUp(self):
        self.client = logIn()

    def test_get_request(self):
        """Tests the behaviour of the view when people visit it."""
        self.client.get(reverse('site_configuration'))

    def test_post_request(self):
        """Tests the behaviour of a view when a POST request is submitted."""
        self.client.post(
            reverse('site_configuration'),
            {'site_name': test_text, 'site_domain': test_text})

 #! TODO
 #  def test_restore


#! TODO
#
# * home
# * subscription
# * user
# * user_content
# * report
# * reports
# * settings
# * saves_and_bookmarks
