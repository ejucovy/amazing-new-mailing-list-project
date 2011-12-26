from Cookie import BaseCookie
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpResponseNotFound
from libopencore import auth
from libopencore.query_project import (get_users_for_project,
                                       admin_post)
from topp.utils.memorycache import cache as memorycache

from opencore.models import Project

def get_user(request):
    try:
        morsel = BaseCookie(request.META['HTTP_COOKIE'])['__ac']
        secret = settings.OPENCORE_SECRET_FILENAME
        secret = auth.get_secret(secret)
        username, hash = auth.authenticate_from_cookie(
            morsel.value, secret)
    except (IOError, KeyError,
            auth.BadCookie, auth.NotAuthenticated):
        return AnonymousUser()
    user, _ = User.objects.get_or_create(username=username)
    return user

class LazyUser(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_user'):
            request._cached_user = get_user(request)
        return request._cached_user

def set_cookie(request, key, val):
    setattr(request, '__cookies_to_set__', 
            getattr(request, '__cookies_to_set__', {}))
    request.__cookies_to_set__[key] = val

def delete_cookie(request, key):
    setattr(request, '__cookies_to_delete__', 
            getattr(request, '__cookies_to_delete__', []))
    request.__cookies_to_delete__.append(key)

class AuthenticationMiddleware(object):
    def process_request(self, request):
        request.__class__.set_cookie = set_cookie
        request.__class__.delete_cookie = delete_cookie
        request.__class__.user = LazyUser()
        return None

    def process_response(self, request, response):
        if hasattr(request, '__cookies_to_set__'):
            for key, val in request.__cookies_to_set__.items():
                response.set_cookie(key, val)
        if hasattr(request, '__cookies_to_delete__'):
            for key in request.__cookies_to_delete__:
                response.delete_cookie(key)
        return response

class Topnav(object):
    def __init__(self, items):
        self.items = items
        self.container = None

    def set_context(self, name, href):
        self.container = {'name': name, 'href': href}

class ContainerMiddleware(object):

    def process_request(self, request):
        setattr(request, 'opencore_context', None)

        if request.META.get("HTTP_X_OPENPLANS_PROJECT") is not None:
            project = request.META.get("HTTP_X_OPENPLANS_PROJECT")
            request.opencore_context = ("projects", project)
            return

        path_info = request.path_info
        path_info = path_info.strip("/").split("/")

        if len(path_info) == 1:
            return
        if path_info[0] == "projects":
            request.opencore_context = ("projects", path_info[1])
        elif path_info[0] == "people":
            request.opencore_context = ("people", path_info[1])

    def inject_topnav_site(self, request, response):
        response.context_data['topnav'] = Topnav([
                ("/people/", "People"),
                ("/projects/", "Projects"),
                ("/projects/create/", "Start a Project"),
                ])
        response.context_data['topnav'].set_context(
            settings.SITE_NAME, "/")
        return response        
    
    def process_template_response(self, request, response):
        context = getattr(request, 'opencore_context', None)
        if not context:
            return self.inject_topnav_site(request, response)

        if context[0] == "projects":
            try:
                project = Project.objects.get(slug=context[1])
            except Project.DoesNotExist:
                return self.inject_topnav_site(request, response)
            if not project.viewable(request):
                return self.inject_topnav_site(request, response)
            if project.manageable(request):
                response.context_data['topnav'] = Topnav([
                        ("/projects/%s/" % context[1], "Summary"),
                        ("/projects/%s/lists/" % context[1], "Mailing Lists"),
                        ("/projects/%s/team/" % context[1], "Team"),
                        ("/projects/%s/manage-team/" % context[1], "Manage Team"),
                        ("/projects/%s/preferences/" % context[1], "Preferences"),
                        ])
            else:
                response.context_data['topnav'] = Topnav([
                        ("/projects/%s/" % context[1], "Summary"),
                        ("/projects/%s/lists/" % context[1], "Mailing Lists"),
                        ("/projects/%s/team/" % context[1], "Team"),
                        ])
                if not project.has_member(request.user):
                    response.context_data['topnav'].items.append(
                        ("/projects/%s/request-membership/" % context[1], 
                         "Join Project"),
                        )
            response.context_data['topnav'].set_context(
                context[1], "/projects/%s/" % context[1]
                )
            return response
        if context[0] == "people":
            response.context_data['topnav'] = Topnav([
                ("/people/%s/" % context[1], "Home"),
                ("/people/%s/profile/" % context[1], "Profile"),
                ("/people/%s/account/" % context[1], "Account"),
                ])
            response.context_data['topnav'].set_context(
                context[1], "/people/%s/" % context[1]
                )
            return response
