from django.conf import settings

from django_nose import FastFixtureTestCase as TestCase


def get_apps():
    apps = {}

    for i, app in enumerate(settings.INSTALLED_APPS):
        apps[app] = i
    return apps


class AppOrderTest(TestCase):
    """Ensures the apps are in the order as required by their authors."""

    def test_forum(self):
        """'forum' goes at the beginning cf.
        https://github.com/ndarville/pony-forum/issues/60.
        """
        apps = get_apps()

        if 'forum' in apps:
            self.assertEquals(apps['forum'], 0)

    def test_django_nose(self):
        """'django_nose' comes after 'South' cf.
        https://github.com/jbalogh/django-nose/blob/master/README.rst#using-with-south.
        """
        apps = get_apps()

        if 'django_nose' in apps and 'South' in apps:
            self.assertTrue(apps['django_nose'] > apps['South'])

    def test_django_admin_bootstrapped(self):
        """'django_admin_bootstrapped comes before 'django.contrib.admin' cf.
        https://github.com/riccardo-forina/django-admin-bootstrapped/blob/master/README.md.
        """
        apps = get_apps()

        if 'django_admin_bootstrapped' and 'django.contrib.admin' in apps:
            self.assertTrue(apps['django_admin_bootstrapped'] < apps['django.contrib.admin'])
