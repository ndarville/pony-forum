"""Tests the views in views.py by passing their functions test arguments."""
import os

from django.core.urlresolvers       import reverse
from django.test.client             import Client

from django_nose                    import FastFixtureTestCase as TestCase


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
            200
        )


class PostTests(TestCase):
    """Test operations with post objects."""
    fixtures = [
        'admin_user.json',
        'users.json',
        'categories.json',
        'threads.json',
        'posts.json'
    ]

    def setUp(self):
        self.client = logIn()

    def test_reply(self):
        self.client = logIn()
        thread_id = 5
        self.client.post(
            reverse('forum.views.reply', args=(thread_id,)),
            {'content': 'Howdy ho.'}
        )
