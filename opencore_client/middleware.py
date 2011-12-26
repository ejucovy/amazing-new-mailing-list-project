from Cookie import BaseCookie
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpResponseNotFound
from libopencore import auth
from libopencore.query_project import (get_users_for_project,
                                       admin_post)
from topp.utils.memorycache import cache as memorycache

class ContainerMiddleware(object):

    def process_request(self, request):
        project = request.META.get("HTTP_X_OPENPLANS_PROJECT")
        setattr(request, 'opencore_context', None)
        setattr(request, 'opencore_container', None)

        if project is not None:
            request.opencore_context = ("projects", project)
            request.opencore_container = "%s.projects" % project

    def process_template_response(self, request, response):
        context = getattr(request, 'opencore_context', None)
        if not context:
            response.context_data['topnav'] = [
                ("/people/", "People"),
                ("/projects/", "Projects"),
                ("/projects/create/", "Start a Project"),
                ]
            return response
        if context[0] == "projects":
            response.context_data['topnav'] = [
                ("/projects/%s/" % context[1], "Summary"),
                ("/projects/%s/manage-team/" % context[1], "Manage Team"),
                ("/projects/%s/preferences/" % context[1], "Preferences"),
                ("/projects/%s/request-membership/" % context[1], "Join Project"),
                ]
            return response
        if context[0] == "people":
            response.context_data['topnav'] = [
                ("/people/%s/" % context[1], "Home"),
                ("/people/%s/profile/" % context[1], "Profile"),
                ("/people/%s/account/" % context[1], "Account"),
                ]
            return response
