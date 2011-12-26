from Cookie import BaseCookie
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpResponseNotFound
from libopencore import auth
from libopencore.query_project import (get_users_for_project,
                                       admin_post)
from topp.utils.memorycache import cache as memorycache

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


class ContainerMiddleware(object):

    def process_request(self, request):
        path_info = request.path_info
        path_info = path_info.strip("/").split("/")
        setattr(request, 'opencore_context', None)
        if len(path_info) == 1:
            return
        if path_info[0] == "projects":
            request.opencore_context = ("projects", path_info[1])
        elif path_info[0] == "people":
            request.opencore_context = ("people", path_info[1])
    
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
