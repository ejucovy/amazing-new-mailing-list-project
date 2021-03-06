from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    'opencore.members.views',

    url(r'^$', 'index_of_members', name='index_of_members'),

    url('^(?P<username>[\w\d-]+)/$', 'member_home', name='member_home'),
    url('^(?P<username>[\w\d-]+)/account/$', 'member_account', 
        name='member_account'),

    url('^(?P<username>[\w\d-]+)/account/project-invites/(?P<project_slug>[\w\d-]+)/$', 'member_project_invites', name='member_project_invites'),

    url('^(?P<username>[\w\d-]+)/account/email-contacts/$',
        'member_email_contacts', name='member_email_contacts'),
    url('^(?P<username>[\w\d-]+)/account/email-contacts/(?P<contact_id>\d+)/$',
        'member_email_contacts_entry', name='member_email_contacts_entry'),

    url('^(?P<username>[\w.@+-]+)/profile/$', 'member_profile', name='member_profile'),
    url('^(?P<username>[\w.@+-]+)/profile-edit/$', 'member_profile_edit', name='member_profile_edit'),

    )
