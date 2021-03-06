from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    'opencore.views',

    url('^$', 'index_of_projects', name='index_of_projects'),
    url('^create/$', 'create_project', name='create_project'),

    ## Project views
    url('^(?P<project_slug>[\w\d-]+)/$', 'project_home', name='project_home'),
    url('^(?P<project_slug>[\w\d-]+)/preferences/$', 'project_preferences', 
        name='project_preferences'),
    url('^(?P<project_slug>[\w\d-]+)/team/$', 'project_team', name='project_team'),
    url('^(?P<project_slug>[\w\d-]+)/manage-team/$', 'project_team_manage', 
        name='project_team_manage'),

    url('^(?P<project_slug>[\w\d-]+)/manage-team/invite/$', 
        'project_team_invite', name='project_team_invite'),
    url('^(?P<project_slug>[\w\d-]+)/manage-team/invite-by-email/$', 
        'project_team_invite_email', name='project_team_invite_email'),

    url('^(?P<project_slug>[\w\d-]+)/request-membership/$', 
        'project_team_request_membership', 
        name='project_team_request_membership'),


    ## API endpoints
    url('^(?P<project_slug>[\w\d-]+)/info\.xml$', 'project_info', name='project_info'),
    url('^(?P<project_slug>[\w\d-]+)/members\.xml$', 'project_info_members',
        name='project_info_members'),
    
    )
