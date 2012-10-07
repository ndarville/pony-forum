import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from forum.models import Category, Thread

c = Category()

class CategoryModelTest(TestCase):
    """Tests Category object."""

    def test_add_category(self):
        # Create Category object
        c = Category()
        title = "Test Category"
        c.title_plain, c.title_html = title, title

        # Save
        c.save()

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
        # Create Thread object
        t = Thread()
        t.category = c
        title = "Test Thread"
        t.title_plain, t.title_html = title, title
        t.creation_date, t.latest_reply_date = datetime.datetime.now(), datetime.datetime.now()
        t.author = User.objects.get(pk=1)

        # Save
        t.save()