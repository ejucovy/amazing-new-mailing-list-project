from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'main.views.home', name='home'),

    url(r'projects/(?P<project_slug>[\w\d-]+)/lists/(?P<list_slug>[\w\d-]+)/$',
        'main.views.mailing_list', name="mailing_list"),

    # url(r'^skel/', include('skel.foo.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
