# If you use this as your local settings file,
# remember to change the name to local_settings.py.

LOCAL_SETTINGS = True
DEBUG = True
INSTALLED_APPS += ('debug_toolbar',)
MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
INTERNAL_IPS = ('127.0.0.1',)

### DATABASES
# Remember to set up the example databases below,
# before you can use them; they are just set-ups to give you an idea
# of what they could be. I have the exact same working config at home.
#
# WARNING: You should *not* leave this formation in the settings.py
# file you upload to your server, as it contains passwords
# to what may be very sensitive and valuable databases
# on the local development environment!
#
# If you only use your databases for testing Pony Forum,
# I guess you don't have much to worry about,
# but better safe than sorry
#
# Google "django local_settings.py" for some ideas on
# how to store your local settings more safely

LOCAL_DB_MYSQL = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'mydb',
        'USER':     'root',
        'PASSWORD': 'mypassword',
        'HOST':     '',
        'PORT':     '',
    }
}

LOCAL_DB_POSTGRESQL = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql_psycopg2',
        'NAME':     'template1',
        'USER':     'postgres',
        'PASSWORD': 'mypassword',
        'HOST':     'localhost',  # Remember this part!
        'PORT':     '',
    }
}

# Database to use:
DATABASES = LOCAL_DB_POSTGRESQ
###

### E-MAIL
# EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

EMAIL_HOST           = 'smtp.gmail.com'
EMAIL_HOST_USER      = 'myusername@gmail.com'
EMAIL_HOST_PASSWORD  = 'mypassword'
EMAIL_PORT           = 587
EMAIL_USE_TLS        = True
EMAIL_SUBJECT_PREFIX = '[Pony Forum] '  # Does not work (anymore?)
###