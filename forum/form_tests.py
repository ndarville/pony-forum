"""Form tests for the `forum` app.

Currently verifies the integrity of the registration scenarios.
"""
from forum.forms import CustomRegistrationForm as Form

from django_nose import FastFixtureTestCase as TestCase


# Valid inputs
valid_regular = {
        'username':  'test user 1',
        'email':     'test1@mail.com',
        'password1': 'password',
        'password2': 'password'
}

# valid_with_email_filter = {
#         'username':  'test user 2',
#         'email':     'test2+filter@mail.com',
#         'password1': 'password',
#         'password2': 'password'
# }

# Invalid inputs
duplicate_email_without_email_filters = {
        'username':  'test user 3',
        'email':     'taken_address@mail.com',
        'password1': 'password',
        'password2': 'password'
}

with_email_filter = {  # delete after +filter enabled
        'username':  'test user 2',
        'email':     'test2+filter@mail.com',
        'password1': 'password',
        'password2': 'password'
}

# duplicate_email_with_one_email_filter = {
#         'username':  'test user 4',
#         'email':     'taken_address+anotherfilter@mail.com',
#         'password1': 'password',
#         'password2': 'password'
# }

# duplicate_email_with_two_email_filters = {
#         'username':  'test user 4',
#         'email':     'another_taken_address+anotherfilter@mail.com',
#         'password1': 'password',
#         'password2': 'password'
# }

mismatched_passwords = {
        'username':  'test user 4',
        'email':     'test3@mail.com',
        'password1': 'password1',
        'password2': 'password2'
}

class RegistrationTest(TestCase):
    """Tests registration scenarios."""
    fixtures = ['registered_users.json']

    def test_valid_regular(self):
        """A regular, valid registration."""
        self.assertEquals(Form(
            valid_regular).is_valid(), True)

    # def test_valid_with_email_filter(self):
    #     """A regular, valid registration where the user provides an """
    #     self.assertEquals(Form(
    #         valid_with_email_filter).is_valid(), True)

    def test_invalid_with_email_filter(self):
        #"""A regular, valid registration where the user provides an """
        """User provides an e-mail address with a +filter in it,
        which is currently unsupported.
        """
        self.assertEquals(Form(
            with_email_filter).is_valid(), False)

    def test_duplicate_email_without_email_filters(self):
        """User registers test1@mail.com.
        Another registers test1@mail.com (or tries to).

        Identifical e-mail addresses are not allowed."""
        self.assertEquals(Form(
            duplicate_email_without_email_filters).is_valid(), False)

    # def test_duplicate_email_with_one_email_filter(self):
    #     """User registers test1@mail.com.
    #     Another registers test1+anotherfilter@mail.com (or tries to).

    #     Identifical e-mail addresses are not allowed,
    #     with or without a +filter in the e-mail addresses.
    #     """
    #     self.assertEquals(Form(
    #         duplicate_email_with_one_email_filter).is_valid(), False)

    # def test_duplicate_email_with_two_email_filters(self):
    #     """User registers test2+filter@mail.com.
    #     Another registers test2+anotherfilter@mail.com (or tries to).

    #     Identifical e-mail addresses are not allowed,
    #     with or without a +filter in the e-mail addresses.
    #     """
    #     self.assertEquals(Form(
    #         duplicate_email_with_two_email_filters).is_valid(), False)

    def test_mismatched_passwords(self):
        """Self-explanatory, no?"""
        self.assertEquals(Form(
            mismatched_passwords).is_valid(), False)
