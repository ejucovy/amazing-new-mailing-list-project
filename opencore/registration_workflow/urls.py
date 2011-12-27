from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',

    url(r'^activate/(?P<activation_key>\w+)/$',
        'opencore.registration_workflow.views.activate',
        {'backend': 'registration.backends.default.DefaultBackend'},
        name='registration_activate'),

    url(r'^register/$',
        'opencore.registration_workflow.views.register',
        name='registration_register'),
    
    (r'', include('registration.auth_urls')),
    )
