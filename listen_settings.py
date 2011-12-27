from settings import *

ROOT_URLCONF = 'listen.urls'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'opencore.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'opencore_client.middleware.SecurityContextMiddleware',
    'opencore_client.middleware.ContainerMiddleware',
)

TEMPLATE_DIRS = (
    
    )
