from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import (HttpResponse,
                         HttpResponseForbidden, 
                         HttpResponseNotFound)
from django.shortcuts import redirect 
from djangohelpers import (rendered_with,
                           allow_http)
from opencore.models import *

@allow_http("GET", "POST")
def index_of_projects(request):
    pass

def _create_project(request):
    pass

@allow_http("GET")
def project_home(request, project_slug):
    project = Project.objects.get(slug=project_slug)
    if not project.viewable(request):
        return HttpResponseForbidden()
    pass

def _edit_project(request):
    pass

@allow_http("GET", "POST")
def project_preferences(request, project_slug):
    project = Project.objects.get(slug=project_slug)
    if not project.viewable(request):
        return HttpResponseForbidden()
    if not project.manageable(request):
        return HttpResponseForbidden()
    pass

@allow_http("GET")
def project_team(request, project_slug):
    project = Project.objects.get(slug=project_slug)
    if not project.viewable(request):
        return HttpResponseForbidden()
    pass

@allow_http("GET", "POST")
def project_team_manage(request, project_slug):
    project = Project.objects.get(slug=project_slug)
    if not project.viewable(request):
        return HttpResponseForbidden()
    if not project.manageable(request):
        return HttpResponseForbidden()
    pass

@allow_http("GET")
@rendered_with("opencore/project_info.xml")
def project_info(request, project_slug):
    project = Project.objects.get(slug=project_slug)
    if not project.viewable(request):
        return HttpResponseForbidden()
    return {}    

@allow_http("GET")
@rendered_with("opencore/project_info_members.xml")
def project_info_members(request, project_slug):
    project = Project.objects.get(slug=project_slug)
    if not project.viewable(request):
        return HttpResponseForbidden()
    return {}
