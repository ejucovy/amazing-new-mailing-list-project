from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    'listen.views',

    url(r'^(?P<list_slug>[\w\d-]+)/moderate/post/(?P<post_id>\d+)/$',
        'mailing_list_moderate_post', name="mailing_list_moderate_post"),

    url(r'^(?P<list_slug>[\w\d-]+)/moderate/subscriber/(?P<subscriber_id>\d+)/$',
        'mailing_list_moderate_subscriber', name="mailing_list_moderate_subscriber"),

    url(r'^(?P<list_slug>[\w\d-]+)/moderate/$',
        'mailing_list_moderate', name="mailing_list_moderate"),

    url(r'^(?P<list_slug>[\w\d-]+)/subscribe/$',
        'request_subscription', name="request_subscription"),

    url(r'^(?P<list_slug>[\w\d-]+)/unsubscribe/$',
        'unsubscribe', name="unsubscribe"),

    url(r'^(?P<list_slug>[\w\d-]+)/post/(?P<post_id>\d+)/$',
        'mailing_list_view_post', name="mailing_list_view_post"),

    url(r'^(?P<list_slug>[\w\d-]+)/$',
        'mailing_list', name="mailing_list"),

    url(r'^$',
        'index_of_mailing_lists', name="index_of_mailing_lists"),
    
    )
