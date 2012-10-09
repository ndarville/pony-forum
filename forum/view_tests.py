"""Tests the views in views.py through the admin interface."""
import os

from django.test import LiveServerTestCase

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def startBrowser(self):
    """Helper function. Starts the test browser.
    Called by setUp at the start of a test.
    """
    if 'TRAVIS' in os.environ:
        # Initialize hidden display for Firefox.
        # Less annoying and allows remote execution.
        display = Display(visible=0, size=(800, 600))
        display.start()

    self.browser = webdriver.Firefox()
    self.browser.implicitly_wait(3)

def stopBrowser(self):
    """Helper function. Stops the test browser.
    Called by setUp at the end of a test.
    """
    self.browser.quit()


class SiteAdminLoginTest(LiveServerTestCase):
    """Simulates an admin logging in to Site Administration in Firefox."""
    fixtures = ['admin_user.json']

    def setUp(self):
        startBrowser(self)

    def tearDown(self):
        stopBrowser(self)

    def test_can_log_in_to_site_administration(self):
        # Opens webbrowser, go to admin page
        self.browser.get(self.live_server_url + '/admin/')

        # Is the 'Django administration' header present?
        # In other words, did we reach the actual log-in page?
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Django administration', body.text)

        # Enter username in log-in form
        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('admin')

        # Enter password
        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('password')

        # Submit
        password_field.send_keys(Keys.RETURN)

        # Assert username and password authenticate
        # directing user to site administration page
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Site administration', body.text)