# Django settings for skel project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

LANGUAGE_CODE = 'en-us'

INTERNAL_IPS = ('127.0.0.1',
                )

SITE_DOMAIN = "localhost:7999"
SITE_NAME = 'OpenCore Site'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# By default urllib, urllib2, and the like have no timeout which can cause
# some apache processes to hang until they are forced kill.
# Before python 2.6, the only way to cause them to time out is by setting
# the default timeout on the global socket
import socket
socket.setdefaulttimeout(5)

import os
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media/')
STATIC_ROOT = os.path.join(PROJECT_PATH, 'static/')
MEDIA_URL = '/media/'
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'common_static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '8l+3aamxj#!@+ul-))li=yma!7p3e@e8cf5qzdma7n=dtyqwiv'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'opencore.middleware.AuthenticationMiddleware',
    'inactive_user_workflow.middleware.CatchInactiveUsersMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'opencore.middleware.ContainerMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, "templates"),
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

ACCOUNT_ACTIVATION_DAYS = 7

BROKER_URL = "django://"

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'registration_defaults',
    'django.contrib.admin',
    'debug_toolbar',
    'djangohelpers',
    'registration',
    'inactive_user_workflow',
    'djcelery',
    'djkombu',
    'opencore',
    'opencore.members',
    'listen',
    'main',
    )
import djcelery
djcelery.setup_loader()

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False
}

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    )


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

LIST_SUBSCRIPTION_MODERATION_POLICIES = [
    ('medium', 'listen.policies.subscription.MediumPolicy'),
    ('open', 'listen.policies.subscription.OpenPolicy'),
    ('closed', 'listen.policies.subscription.ClosedPolicy'),
    ]
LIST_POST_MODERATION_POLICIES = [
    ('medium', 'listen.policies.post.MediumPolicy'),
    ('open', 'listen.policies.post.OpenPolicy'),
    ('closed', 'listen.policies.post.ClosedPolicy'),
    ]

# import local settings overriding the defaults
try:
    from local_settings import *
except ImportError:
    try:
        from mod_python import apache
        apache.log_error( "local settings not available", apache.APLOG_NOTICE )
    except ImportError:
        import sys
        sys.stderr.write( "local settings not available\n" )
else:
    try:
        INSTALLED_APPS += LOCAL_INSTALLED_APPS
    except NameError:
        pass
    try:
        MIDDLEWARE_CLASSES += LOCAL_MIDDLEWARE_CLASSES
    except NameError:
        pass
