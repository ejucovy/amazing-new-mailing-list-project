from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'main.views.home', name='home'),

    url(r'projects/(?P<project_slug>[\w\d-]+)/lists/', include('listen.urls')),
    url(r'projects/', include('opencore.urls')),
    url(r'people/', include('opencore.members.urls')),

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
                           
    url(r'^admin/', include(admin.site.urls)),
    )
