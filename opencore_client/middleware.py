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


@memorycache(600)
def _fetch_policy(project):
    import elementtree.ElementTree as etree
    url = "%s/projects/%s/info.xml" % (
        settings.OPENCORE_SERVER, project)
    admin_info = auth.get_admin_info(settings.OPENCORE_ADMIN_FILE)
    resp, content = admin_post(url, *admin_info)
    assert resp['status'] == '200'
    tree = etree.fromstring(content)
    policy = tree[0].text
    return policy

def get_security_policy(request):
    if hasattr(request, '_cached_opencore_policy'):
        return request._cached_opencore_policy
    policy = _fetch_policy(request.META['HTTP_X_OPENPLANS_PROJECT'])
    request._cached_opencore_policy = policy
    return policy

@memorycache(600)
def _fetch_user_roles(project):
    admin_info = auth.get_admin_info(settings.OPENCORE_ADMIN_FILE)
    users = get_users_for_project(project,
                                  settings.OPENCORE_SERVER,
                                  admin_info)
    return users

def get_project_members(request):
    if hasattr(request, '_cached_opencore_project_members'):
        return request._cached_opencore_project_members

    users = _fetch_user_roles(request.META['HTTP_X_OPENPLANS_PROJECT'])
    members = []
    for member in users:
        members.append(member['username'])
    members = sorted(members)
    request._cached_opencore_project_members = members
    return members

class SecurityContextMiddleware(object):
    def process_request(self, request):
        request.get_project_members = lambda: get_project_members(request)
        request.get_security_policy = lambda: get_security_policy(request)
        
