from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',

    url('^(?P<activation_key>\w+)/$',
        'opencore.contact_manager.views.confirm_secondary_email_contact',
        name='confirm_secondary_email_contact'),

    )
