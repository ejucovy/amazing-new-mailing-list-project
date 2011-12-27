from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    url('^welcome/(?P<activation_key>\w+)/$',
        'opencore.contact_manager.views.confirm_initial_email_contact',
        name='confirm_initial_email_contact'),

    url('^join/(?P<activation_key>\w+)/$',
        'opencore.contact_manager.views.confirm_temporary_account_email_contact',
        name='confirm_temporary_account_email_contact'),

    url('^(?P<activation_key>\w+)/$',
        'opencore.contact_manager.views.confirm_secondary_email_contact',
        name='confirm_secondary_email_contact'),

    )
