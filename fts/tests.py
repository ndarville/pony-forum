from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class SiteAdminLoginTest(LiveServerTestCase):
    """Foo."""
    fixtures = ['admin_user.json']

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_can_create_new_polls_via_admin_site(self):
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

        # TODO: use the admin site to create a Polls
        self.fail('Finish this test')