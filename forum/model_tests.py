"""Model tests for the `forum` app.

Currently verifies that creation of the three major model classes
works. Tests `models.py`.
"""
import datetime

from django.contrib.auth.models import User
from django.utils import timezone

from django_nose import FastFixtureTestCase as TestCase

from forum.models import Category, Thread, Post, Report


def mkuser():
    """Helper function for making users."""
    u, created = User.objects.get_or_create(username='admin')
    if created:
        u.set_password('password')
        u.is_superuser = True
        u.is_staff = True
        u.save()

    return u

def mkcategory(title="Test Category"):
    """Helper function for making categories."""
    c = Category()

    c.title_plain, c.title_html = title, title
    c.save()

    return c

def mkthread(title="Test Thread",
             creation_date=datetime.datetime.now(),
             latest_reply_date=datetime.datetime.now()):
    """Helper function for making threads."""
    t = Thread()

    t.title_plain, t.title_html = title, title
    t.creation_date = creation_date
    t.latest_reply_date = latest_reply_date
    t.category = mkcategory()
    t.author = mkuser()
    t.save()

    return t

def mkpost(content="Test post.",
           creation_date=datetime.datetime.now()):
    """Helper function for making posts."""
    p = Post()

    # _plain == _html, since the conversion happens in views.py,
    # which the object creation is not run through
    p.content_plain, p.content_html = content, content
    p.creation_date = creation_date
    p.author = mkuser()
    p.thread = mkthread()
    p.save()

    return p

def mkreport(reason="Iiiinsolence!",
             creation_date=datetime.datetime.now()):
    """Helper function for making reports."""
    r = Report()
    r.reason_short = reason
    r.reason_long_plain = reason+"111"
    r.reason_long_html = "<p>"+reason+"111"+"</p>"
    r.creation_date = creation_date
    r.author = mkuser()
    r.thread = mkthread()
    r.save()

    return r


class CategoryModelTest(TestCase):
    """Tests Category object."""
    def test_add_category(self):
        """Test the creation of a Category object."""
        # Create Category object
        title = "Test Category"
        c = mkcategory(title)

        # Retrieve category from database
        all_categories = Category.objects.all()
        self.assertEquals(len(all_categories), 1)
        only_category_in_db = all_categories[0]
        self.assertEquals(only_category_in_db, c)

        # Check the two saved fields from before
        self.assertEquals(only_category_in_db.title_plain, title)
        self.assertEquals(only_category_in_db.title_html, title)


class ThreadModelTest(TestCase):
    """Tests Thread object."""
    def test_create_thread(self):
        """Test the creation of a Thread object."""
        title = "Test Thread"
        now = datetime.datetime.now()
        t = mkthread(title, now, now)

        # Retrieve threads from database
        all_threads = Thread.objects.all()
        self.assertEquals(len(all_threads), 1)
        only_thread_in_db = all_threads[0]
        self.assertEquals(only_thread_in_db, t)

        # Check the four saved fields from before
        self.assertEquals(only_thread_in_db.title_plain, title)
        self.assertEquals(only_thread_in_db.title_html, title)
        self.assertEquals(only_thread_in_db.creation_date, now)
        self.assertEquals(only_thread_in_db.latest_reply_date, now)


class PostModelTest(TestCase):
    """Tests Post object."""
    def test_create_post(self):
        """Test the creation of a Post object."""
        content = "Test post."
        now = datetime.datetime.now()
        p = mkpost(content, now)

        # Retrieve threads from database
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)
        only_post_in_db = all_posts[0]
        self.assertEquals(only_post_in_db, p)

        # Check the three saved fields from before
        self.assertEquals(only_post_in_db.content_plain, content)
        self.assertEquals(only_post_in_db.content_html, content)
        self.assertEquals(only_post_in_db.creation_date, now)


class ReportModelTest(TestCase):
    """Tests Report object."""
    def test_create_report(self):
        """Test the creation of a Report object."""
        reason = "Iiiinsolence!"
        now = datetime.datetime.now()
        r = mkreport(reason, now)

        # Retrieve reports from database
        all_reports = Report.objects.all()
        self.assertEquals(len(all_reports), 1)
        only_report_in_db = all_reports[0]
        self.assertEquals(only_report_in_db, r)

        # Check the two saved fields from before
        self.assertEquals(only_report_in_db.reason_short, reason)
        self.assertEquals(only_report_in_db.reason_long_plain, reason+"111")
        self.assertEquals(
            only_report_in_db.reason_long_html,
            "<p>"+reason+"111"+"</p>")
        self.assertEquals(only_report_in_db.creation_date, now)
