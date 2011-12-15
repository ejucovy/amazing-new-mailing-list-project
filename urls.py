from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'main.views.home', name='home'),


    url(r'projects/(?P<project_slug>[\w\d-]+)/lists/(?P<list_slug>[\w\d-]+)/moderate/$',
        'main.views.mailing_list_moderate', name="mailing_list_moderate"),

    url(r'projects/(?P<project_slug>[\w\d-]+)/lists/(?P<list_slug>[\w\d-]+)/$',
        'main.views.mailing_list', name="mailing_list"),

    url(r'projects/(?P<project_slug>[\w\d-]+)/lists/$',
        'main.views.index_of_mailing_lists', name="index_of_mailing_lists"),

    (r'^accounts/', include('inactive_user_workflow.urls')),
    
    # url(r'^skel/', include('skel.foo.urls')),

    url(r'^admin/', include(admin.site.urls)),
    )
