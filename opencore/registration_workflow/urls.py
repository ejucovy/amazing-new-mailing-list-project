from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',

    url(r'^register/$',
        'opencore.registration_workflow.views.register',
        name='registration_register'),
    
    (r'', include('registration.auth_urls')),
    )
