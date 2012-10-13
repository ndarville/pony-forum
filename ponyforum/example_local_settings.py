"""
If you use this as your local settings file,
remember to change the name to local_settings.py.

Don't make the mistake of committing this file
containing your delicate passwords to a repo.

If you do, you can try this:
    git reset --soft HEAD^
    git push -f

This reverts back to the second-most recent commit.

It is not recommended for repos that other people use.
"""
import os


LOCAL_SETTINGS = True
DEBUG = True

### DATABASES
# These are example databases that don't work out of the box.
# You will have to configure your own.
#
# WARNING: You should *not* leave this information in the settings.py
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
        'NAME':     'mydb',        ## Change this value to your own
        'USER':     'root',
        'PASSWORD': 'mypassword',  ## Change this value to your own
        'HOST':     '',
        'PORT':     '',
    }
}

LOCAL_DB_POSTGRESQL = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql_psycopg2',
        'NAME':     'mydb',       # Change this value to your own;
                                  #     leave blank on OS X
        'USER':     'postgres',   # Leave blank on OS X
        'PASSWORD': 'mypassword', # Change this value to your own;
                                  #     leave blank on OS X
        'HOST':     'localhost',  # Remember this part!
        'PORT':     '',
    }
}

# Database to use; note that PF only officially supports postgreSQL
if os.name == "nt":  # OS is Windows
    DATABASES = LOCAL_DB_MYSQL
else:  # Not Windows: Linux/UNIX-based such as Mac OS, Ubuntu, etc.
    DATABASES = LOCAL_DB_POSTGRESQL
###

### E-MAIL
# Here is a rather simple guide for setting up a local e-mail server:
# http://tinyurl.com/cprffxb
#
# Otherwise, use this guide for Gmail accounts:
# http://sontek.net/using-gmail-to-send-e-mails-from-django

EMAIL_HOST           = 'smtp.gmail.com'
EMAIL_HOST_USER      = 'myusername@gmail.com'
EMAIL_HOST_PASSWORD  = 'mypassword'
EMAIL_PORT           = 587
EMAIL_USE_TLS        = True
EMAIL_SUBJECT_PREFIX = '[Pony Forum] '  # Does not work (anymore?)
DEFAULT_FROM_EMAIL   = 'noreply@equestria.pony'

if EMAIL_HOST_USER == "myusername@gmail.com":
    EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
###

### DJANGO-DEBUG-TOOLBAR
if DEBUG:
    DEBUG_TOOLBAR_PANELS = (
       'debug_toolbar.panels.version.VersionDebugPanel',
       'debug_toolbar.panels.timer.TimerDebugPanel',
       'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
       'debug_toolbar.panels.headers.HeaderDebugPanel',
       'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
       'debug_toolbar.panels.template.TemplateDebugPanel',
       'debug_toolbar.panels.sql.SQLDebugPanel',
       'debug_toolbar.panels.signals.SignalDebugPanel',
       'debug_toolbar.panels.logger.LoggingPanel',
#      'cache_panel.panel.CacheDebugPanel',
    )
###