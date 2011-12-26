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
