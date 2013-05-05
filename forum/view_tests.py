"""Tests the views in views.py by passing their functions test arguments."""
import json
import os

from django.core.urlresolvers import reverse
from django.test.client       import Client
from django.test.utils        import override_settings

from django_nose              import FastFixtureTestCase as TestCase

from forum.models             import Category, Thread, Post, Report


test_text = "Howdy ho."

# Determines count of thread and post objects
# and ID of test category, threads, and post
with open('forum/fixtures/forum_example.json') as f:
    for x in json.load(f):
        if x['model'] == 'forum.category':
            test_category_id = x['pk']
        elif x['model'] == 'forum.thread':
            if x['fields']['title_plain'] == 'Merge Thread 1':
                merge_thread_1_id = x['pk']
            elif x['fields']['title_plain'] == 'Merge Thread 2':
                merge_thread_2_id = x['pk']
        elif x['model'] == 'forum.post':
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
        response = self.client.post(
            reverse('login'),
            {'username': 'admin', 'password': 'password'},
            follow=True)
        self.assertEqual(response.status_code, 200)


class CategoryTests(TestCase):
    """Tests operations with categories."""
    fixtures = ['admin_user.json', 'forum_example.json']

    def test_get(self):
        """Tests the display of a category."""
        response = self.client.get(
            reverse('forum.views.category', args=(test_category_id,)))
        self.assertEqual(response.status_code, 200)

    def test_add(self):
        """Tests the addition of a category."""
        self.client = logIn()
        response = self.client.post(
            reverse('forum.views.add'), {'title': test_text},
            follow=True)
        self.assertEqual(response.status_code, 200)


class ThreadTests(TestCase):
    """Tests operations with threads."""
    fixtures = ['forum_example.json']

    def setUp(self):
        self.client = logIn()

    def test_get(self):
        """Tests the display of a thread."""
        response = self.client.get(
            reverse('forum.views.thread', args=(test_thread_id,)))
        self.assertEqual(response.status_code, 200)

    def test_show_posts_by_author(self):
        """Tests the display of posts by a specific user in a thread."""
        response = self.client.get(
            reverse(
                'forum.views.thread',
                args=(test_category_id, test_user_id,)))
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        """Tests creation of thread."""
        response = self.client.post(
            reverse('forum.views.create', args=(test_category_id,)),
            {'title': test_text, 'content': test_text},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_merge(self):
        """Tests locking of thread."""
        response = self.client.post(
            reverse('forum.views.merge_thread', args=(merge_thread_1_id,)),
            {'other-thread-id':   merge_thread_2_id,
             'new-thread-title': 'Merge Thread 3'},
             follow=True)
        self.assertEqual(response.status_code, 200)

    def test_moderate(self):
        """Tests moderation of thread."""
        response = self.client.post(
            reverse('forum.views.moderate_thread', args=(test_thread_id,)),
            {'lock': 'Lock', 'title': test_text},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_remove(self):
        """Tests removal of a thread."""
        response = self.client.post(
            reverse(
                'forum.views.remove',
                kwargs={'object_id': test_thread_id, 'object_type': 'thread'}),
            {'remove': 'Remove'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_restore(self):
        """Tests restore of a thread."""
        response = self.client.post(
            reverse(
                'forum.views.remove',
                kwargs={'object_id': test_thread_id, 'object_type': 'thread'}),
            {'restore': 'Restore'},
            follow=True)
        self.assertEqual(response.status_code, 200)


class PostTests(TestCase):
    """Test operations with posts."""
    fixtures = ['forum_example.json']

    def setUp(self):
        self.client = logIn()

    def test_get(self):
        """Tests the display of a post."""
        response = self.client.get(
            reverse('forum.views.post', args=(test_post_id,)))
        self.assertEqual(response.status_code, 200)

    def test_reply(self):
        """Tests creation of a post."""
        response = self.client.post(
            reverse('forum.views.reply', args=(test_thread_id,)),
            {'content': test_text},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_edit(self):
        """Tests editing of a post."""
        response = self.client.post(
            reverse('forum.views.edit', args=(test_post_id,)),
            {'content': test_text},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_remove(self):
        """Tests removal of a post."""
        response = self.client.post(
            reverse(
                'forum.views.remove',
                kwargs={'object_id': test_post_id, 'object_type': 'post'}),
            {'remove': 'Remove'},
            follow=True)
        self.assertEqual(response.status_code, 200)


class ReportTests(TestCase):
    """Tests operations related to reports."""
    fixtures = ['admin_user.json', 'forum_example.json']

    def setUp(self):
        self.client = logIn()

    def test_report_thread(self):
        """Tests the reporting of a thread."""
        response = self.client.post(
            reverse(
                'forum.views.report',
                kwargs={'object_id': test_thread_id, 'object_type': 'thread'}),
            {'title': test_text, 'content': test_text, 'submit': 'submit'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_report_post(self):
        """Tests the reporting of a post."""
        response = self.client.post(
            reverse(
                'forum.views.report',
                kwargs={'object_id': test_post_id, 'object_type': 'post'}),
            {'title': test_text, 'content': test_text, 'submit': 'submit'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_get(self):
        """Tests the display of reports."""
        response = self.client.get(reverse('forum.views.reports'))
        self.assertEqual(response.status_code, 200)

    # def test_dismiss_thread_report(self):
    #     """Tests the dismissal of a thread report."""

    # def test_dismiss_post_report(self):
    #     """Tests the dismissal of a post report."""


class HomeTests(TestCase):
    """Test displays of the home view."""
    fixtures = ['admin_user.json', 'forum_example.json']

    def test_home_admin_user(self):
        """Tests the behaviour of the view when a logged-in admin visits."""
        self.client = logIn(username='admin', password='password')
        response = self.client.get(reverse('forum.views.home'))
        self.assertEqual(response.status_code, 200)

    def test_home_anonymous_user(self):
        """Tests the behaviour of the view when a logged-in admin visits."""
        response = self.client.get(reverse('forum.views.home'))
        self.assertEqual(response.status_code, 200)


class UserTests(TestCase):
    """Tests display of user and overview of user contens."""
    fixtures = ['forum_example.json']

    def setUp(self):
        self.client = logIn()

    def test_user(self):
        """Tests the display of a user's page."""
        self.client.get(reverse('forum.views.user', args=(test_user_id,)))

    def test_user_content(self):
        """Tests the display of a user's contens."""
        response = self.client.get(
            reverse('forum.views.user_content', args=(test_user_id,)))
        self.assertEqual(response.status_code, 200)


class NonJsTests(TestCase):
    """Tests operations related to the nonjs view."""
    fixtures = ['admin_user.json', 'forum_example.json']

    def setUp(self):
        self.client = logIn()

    def test_user_follow_nonjs(self):
        """Tests following a user."""
        response = self.client.post(
            reverse('forum.views.nonjs', args=('follow', test_user_id,)),
            {'action': 'follow'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_user_unfollow_nonjs(self):
        """Tests unfollowing a user."""
        response = self.client.post(
            reverse('forum.views.nonjs', args=('follow', test_user_id,)),
            {'action': 'unfollow'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_user_ignore_nonjs(self):
        """Tests adding a user to shit list."""
        response = self.client.post(
            reverse('forum.views.nonjs', args=('ignore', test_user_id,)),
            {'action': 'ignore'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_user_unignore_nonjs(self):
        """Tests removing a user from shit list."""
        response = self.client.post(
            reverse('forum.views.nonjs', args=('ignore', test_user_id,)),
            {'action': 'unignore'},
            follow=True)

    def test_sticky(self):
        """Tests the stickying of a thread."""
        response = self.client.post(
            reverse('forum.views.nonjs', args=('sticky', test_thread_id,)),
            {'action': 'sticky'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_unsticky(self):
        """Tests the unstickying of a thread."""
        response = self.client.post(
            reverse('forum.views.nonjs', args=('sticky', test_thread_id,)),
            {'action': 'unsticky'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_lock(self):
        """Tests the locking of a thread."""
        response = self.client.post(
            reverse('forum.views.nonjs', args=('lock', test_thread_id,)),
            {'action': 'lock'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_unlock(self):
        """Tests the unlocking of a thread."""
        response = self.client.post(
            reverse('forum.views.nonjs', args=('lock', test_thread_id,)),
            {'action': 'unlock'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_subscribe(self):
        """Tests the subscription of a thread."""
        response = self.client.post(
            reverse('forum.views.nonjs', args=('subscribe', test_thread_id,)),
            {'action': 'subscribe'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_unsubscribe(self):
        """Tests the unsubscription of a thread."""
        response = self.client.post(
            reverse('forum.views.nonjs', args=('subscribe', test_thread_id,)),
            {'action': 'unsubscribe'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_bookmark(self):
        """Tests the bookmarking of a thread."""
        response = self.client.post(
            reverse('forum.views.nonjs', args=('bookmark', test_thread_id,)),
            {'action': 'bookmark'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_unbookmark(self):
        """Tests the unbookmarking of a thread."""
        response = self.client.post(
            reverse('forum.views.nonjs', args=('bookmark', test_thread_id,)),
            {'action': 'unbookmark'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_save(self):
        """Tests the saving of a post."""
        response = self.client.post(
            reverse('forum.views.nonjs', args=('save', test_post_id,)),
            {'action': 'save'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_unsave(self):
        """Tests the unsaving of a post."""
        response = self.client.post(
            reverse('forum.views.nonjs', args=('save', test_post_id,)),
            {'action': 'unsave'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_thank(self):
        """Tests the thanking of an author for a post."""
        response = self.client.post(
            reverse('forum.views.nonjs', args=('thank', test_post_id,)),
            {'action': 'thank'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_unthank(self):
        """Tests the unthanking of an author for a post."""
        response = self.client.post(
            reverse('forum.views.nonjs', args=('thank', test_post_id,)),
            {'action': 'unthank'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_agree(self):
        """Tests the agreeing with an author for a post."""
        response = self.client.post(
            reverse('forum.views.nonjs', args=('agree', test_post_id,)),
            {'action': 'agree'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_unagree(self):
        """Tests the unagreeing with an author for a post."""
        response = self.client.post(
            reverse('forum.views.nonjs', args=('agree', test_post_id,)),
            {'action': 'unagree'},
            follow=True)
        self.assertEqual(response.status_code, 200)


class CoeditorTests(TestCase):
    """Test operations related to the manage_coeditors views."""
    fixtures = ['forum_example.json']

    def setUp(self):
        self.client = logIn()

    def test_get_request(self):
        """Tests the behaviour of the view when people visit it."""
        response = self.client.get(
            reverse('forum.views.manage_coeditors',
                args=(test_thread_id,)))
        self.assertEqual(response.status_code, 200)

    def test_search(self):
        """Tests the search for users based on a username query."""
        pass


class CoeditorTestsNonJs(TestCase):
    """Test operations related to the manage_coeditors_nonjs views."""
    fixtures = ['forum_example.json']

    def setUp(self):
        self.client = logIn()

    def test_get_request(self):
        """Tests the behaviour of the view when people visit it."""
        response = self.client.get(
            reverse('forum.views.manage_coeditors_nonjs',
                args=(test_thread_id, test_user_id,)))
        self.assertEqual(response.status_code, 200)

    def test_promote_coeditor(self):
        """Tests the promotion of a co-editor."""
        response = self.client.post(
            reverse('forum.views.manage_coeditors_nonjs',
                args=(test_thread_id, test_user_id)),
            {'action': 'Appoint as co-editor'},
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_demote_coeditor(self):
        """Tests the demotion of a co-editor."""
        response = self.client.post(
            reverse('forum.views.manage_coeditors_nonjs',
                args=(test_thread_id, test_user_id)),
            {'action': 'Remove as co-editor'},
            follow=True)
        self.assertEqual(response.status_code, 200)


class SettingsConfigurationTests(TestCase):
    """Test operations related to the settings view."""
    fixtures = ['admin_user.json']

    def setUp(self):
        self.client = logIn()

    def test_get_request(self):
        """Tests the behaviour of the view when people visit it."""
        response = self.client.get(reverse('forum.views.settings'))
        self.assertEqual(response.status_code, 200)

    def test_post_request(self):
        """Tests the behaviour of a view when a POST request is submitted."""
        response = self.client.post(
            reverse('forum.views.settings'),
            #! TODO
            #  Different variations of settings
            {'has_dyslexia': 'Y', 'auto_subscribe': 'N'},
            follow=True)
        self.assertEqual(response.status_code, 200)


class AccountTests(TestCase):
    """Tests operations related to the accounts back-end."""
    fixtures = ['admin_user.json']

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.dummy.EmailBackend')
    def test_register_user(self):
        """Tests registering a user."""
        response = self.client.post(
            reverse('forum.views.custom_register'), {
                'username':  'Foo',
                'email':     'contact@example.com',
                'password1': 'password',
                'password2': 'password'},
                follow=True)
        self.assertEqual(response.status_code, 200)

    def test_log_in_user(self):
        """Tests logging a user in."""
        response = self.client.post(
            reverse('django.contrib.auth.views.login'),
            {'username': 'admin', 'password': 'password'},
            follow=True)
        self.assertEqual(response.status_code, 200)


class SiteConfigurationTests(TestCase):
    """Test operations related to the site configuration view."""
    fixtures = ['admin_user.json']

    def setUp(self):
        self.client = logIn()

    def test_get_request(self):
        """Tests the behaviour of the view when people visit it."""
        response = self.client.get(reverse('site_configuration'))
        self.assertEqual(response.status_code, 200)

    def test_post_request(self):
        """Tests the behaviour of a view when a POST request is submitted."""
        response = self.client.post(
            reverse('site_configuration'),
            {'site_name': test_text, 'site_domain': test_text},
            follow=True)
        self.assertEqual(response.status_code, 200)


# * report dismissal

# * Different types of visitors:
#     * Admin
#     * Regular, authorized user
#     * Anonymous, unauthorized visitor
