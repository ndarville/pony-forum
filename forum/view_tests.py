"""Tests the views in views.py by passing their functions test arguments."""
import os

from django.core.urlresolvers       import reverse
from django.test.client             import Client

from django_nose                    import FastFixtureTestCase as TestCase


test_thread_id = 3

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


class CategoryTests(TestCase):
    """Tests operations with category objects."""
    fixtures = ['admin_user.json']

    def test_add(self):
        self.client = logIn()
        self.client.post(
            reverse('forum.views.add', args=()),
            {'title': 'Test Category'}
        )


class PostTests(TestCase):
    """Test operations with post objects."""
    fixtures = ['forum_example.json']

    def setUp(self):
        self.client = logIn()

    def test_reply(self):
        """Tests creation of a post object."""
        self.client = logIn()
        self.client.post(
            reverse('forum.views.reply', args=(test_thread_id,)),
            {'content': 'Howdy ho.'}
        )
