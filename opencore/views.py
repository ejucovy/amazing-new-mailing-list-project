from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import (HttpResponse,
                         HttpResponseForbidden, 
                         HttpResponseNotFound)
from django.shortcuts import redirect 
from djangohelpers import (rendered_with,
                           allow_http)
from opencore.models import *
from opencore.forms import (ProjectForm, 
                            TeamForm)

@allow_http("GET", "POST")
def index_of_projects(request):
    pass

@allow_http("GET", "POST")
@rendered_with("opencore/create_project.html")
def create_project(request):
    if request.method == "GET":
        form = ProjectForm()
        return locals()
    form = ProjectForm(request.POST)
    if not form.is_valid():
        return locals()
    project = form.save(request.user)
    messages.success(request, "Your project has been created.  Good job.")
    return redirect(project)    

@allow_http("GET")
@rendered_with("opencore/project_home.html")
def project_home(request, project_slug):
    project = Project.objects.get(slug=project_slug)
    if not project.viewable(request):
        return HttpResponseForbidden()
    return locals()

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
@rendered_with("opencore/project_team_manage.html")
def project_team_manage(request, project_slug):
    project = Project.objects.get(slug=project_slug)
    if not project.viewable(request):
        return HttpResponseForbidden()
    if not project.manageable(request):
        return HttpResponseForbidden()
    if request.method == "GET":
        form = TeamForm(project)
        return locals()
    form = TeamForm(project, data=request.POST)
    if not form.is_valid():
        return locals()
    memberships = form.save()
    messages.success(request, "Modified %s memberships" % len(memberships))
    return redirect(project)


@allow_http("GET")
@rendered_with("opencore/project_info.xml")
def project_info(request, project_slug):
    project = Project.objects.get(slug=project_slug)
    if not project.viewable(request):
        return HttpResponseForbidden()
    return locals()

@allow_http("GET")
@rendered_with("opencore/project_info_members.xml")
def project_info_members(request, project_slug):
    project = Project.objects.get(slug=project_slug)
    if not project.viewable(request):
        return HttpResponseForbidden()
    return locals()
