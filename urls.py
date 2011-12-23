from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'^$', 'main.views.home', name='home'),


    url(r'projects/(?P<project_slug>[\w\d-]+)/lists/(?P<list_slug>[\w\d-]+)/moderate/post/(?P<post_id>\d+)/$',
        'main.views.mailing_list_moderate_post', name="mailing_list_moderate_post"),
    url(r'projects/(?P<project_slug>[\w\d-]+)/lists/(?P<list_slug>[\w\d-]+)/moderate/subscriber/(?P<subscriber_id>\d+)/$',
        'main.views.mailing_list_moderate_subscriber', name="mailing_list_moderate_subscriber"),

    url(r'projects/(?P<project_slug>[\w\d-]+)/lists/(?P<list_slug>[\w\d-]+)/moderate/$',
        'main.views.mailing_list_moderate', name="mailing_list_moderate"),

    url(r'projects/(?P<project_slug>[\w\d-]+)/lists/(?P<list_slug>[\w\d-]+)/subscribe/$',
        'main.views.request_subscription', name="request_subscription"),

    url(r'projects/(?P<project_slug>[\w\d-]+)/lists/(?P<list_slug>[\w\d-]+)/unsubscribe/$',
        'main.views.unsubscribe', name="unsubscribe"),

    url(r'projects/(?P<project_slug>[\w\d-]+)/lists/(?P<list_slug>[\w\d-]+)/$',
        'main.views.mailing_list', name="mailing_list"),

    url(r'projects/(?P<project_slug>[\w\d-]+)/lists/$',
        'main.views.index_of_mailing_lists', name="index_of_mailing_lists"),

    (r'^accounts/', include('registration.backends.default.urls')),
    
    url(r'^accounts/inactive/$',
        direct_to_template,
        {'template': 'registration/inactive_user.html'},
        name='inactive-user'),

    url(r'^accounts/resend-confirmation/$',
        'inactive_user_workflow.views.resend_confirmation_email',
        name='resend-user-confirmation'),
    url(r'^accounts/login/$',
        'inactive_user_workflow.views.login.login',
        {'template_name': 'registration/login.html'},
        name='auth_login'),
                           
    # url(r'^skel/', include('skel.foo.urls')),

    url(r'^admin/', include(admin.site.urls)),
    )
