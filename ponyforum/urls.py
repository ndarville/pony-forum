from django.conf                 import settings as project_settings
from django.conf.urls.defaults   import patterns, include, url
from django.contrib              import admin
from django.views.generic.simple import redirect_to

from forum.forms import CustomRegistrationForm


admin.autodiscover()

urlpatterns = patterns('forum.views',
    (r'^$',                                      'home'),
#   (r'^reports/$',                              'reports'),
#   (r'^search/$',                               'search', name='search'),
#   (r'^subscriptions/$',                        'subscriptions'),
#   (r'^subscriptions/js/$',                     'subscriptions_js'),
#   (r'^subscriptions/nonjs/$',                  'subscriptions_nonjs'),
    (r'^bookmarks/$',                            'saves_and_bookmarks',
                                                    {'object_type': 'bookmark'},
                                                    'bookmarks'),
    (r'^saves/$',                                'saves_and_bookmarks',
                                                    {'object_type': 'save'},
                                                    'saves'),
    (r'^search/$',                               'search'),
    url(r'^' + getattr(project_settings, 'SITE_CONFIGURATION_URL',
                                                 '/configuration/')[1:] + '$',
                                                 'site_configuration',
                                                  name='site_configuration'),

#   Category
    (r'^category/add/$',                         'add'),
    (r'^category/(?P<category_id>\d+)/create/$', 'create'),
#   (r'^category/(?P<category_id>\d+)/merge/$',  'merge'),
    (r'^category/(?P<category_id>\d+)/$',        'category'),

#   Thread
    (r'^thread/(?P<thread_id>\d+)/reply/$',      'reply'),
    (r'^thread/js/$',                            'thread_js'),
#   (r'^thread/nonjs/$',                         'thread_nonjs'),
    (r'^thread/(?P<thread_id>\d+)/lock/$',       'lock_thread'),
    (r'^thread/(?P<thread_id>\d+)/sticky/$',     'sticky_thread'),
    (r'^thread/(?P<thread_id>\d+)/merge/$',      'merge_thread'),
    (r'^thread/(?P<thread_id>\d+)/move/$',       'move_thread'),
    (r'^thread/(?P<thread_id>\d+)/moderate/$',   'moderate_thread'),
#   (r'^thread/(?P<object_id>\d+)/report/$',     'report',
#                                                   {'object_type': 'thread'},
#                                                   'report_thread'),
    (r'^thread/(?P<object_id>\d+)/remove/$',     'remove',
                                                    {'object_type': 'thread'},
                                                    'remove_thread'),
    (r'^thread/(?P<thread_id>\d+)/$',            'thread',
                                                    {'author_id': 'Everyone'}),
	(r'^thread/(?P<thread_id>\d+)/author/(?P<author_id>\d+)/$', 'thread'),

#   Post
    (r'^post/(?P<post_id>\d+)/edit/$',           'edit'),
#   (r'^post/(?P<object_id>\d+)/report/$',       'report',
#                                                   {'object_type': 'post'},
#                                                   'report_post'),
    (r'^post/(?P<object_id>\d+)/remove/$',       'remove',
                                                    {'object_type': 'post'},
                                                    'remove_post'),
    (r'^post/(?P<post_id>\d+)/$',                'post'),

#   User
    (r'^user/js/$',                              'user_js'),
    (r'^user/nonjs/$',                           'user_nonjs'),
    (r'^user/(?P<user_id>\d+)/threads/$',        'user_content',
                                                     {'object_type': 'thread'},
                                                     'user_threads'),
    (r'^user/(?P<user_id>\d+)/posts/$',          'user_content',
                                                     {'object_type': 'post'},
                                                     'user_posts'),
    (r'^user/(?P<user_id>\d+)/$',                'user'),

#   Accounts
    url(r'^' + getattr(project_settings, 'LOGIN_URL',
                                                 '/accounts/login/')[1:] + '$',
                                                 'custom_login',
                                                  name='login'),
    url(r'^' + getattr(project_settings, 'LOGOUT_URL',
                                                 '/accounts/logout/')[1:] + '$',
                                                 'custom_logout',
                                                  name='logout'),
    url(r'^' + getattr(project_settings, 'REGISTRATION_URL',
                                                 '/accounts/register/')[1:] + '$',
                                                 'custom_register',
                                                {'form_class':
                                                  CustomRegistrationForm},
                                                  name='register'),
    (r'^accounts/settings/$',                    'settings'),
)

urlpatterns += patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/',     include(admin.site.urls)),
    url(r'^accounts/',  include('registration.backends.default.urls')),
)