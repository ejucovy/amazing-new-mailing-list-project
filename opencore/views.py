from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
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
@rendered_with("opencore/index_of_projects.html")
def index_of_projects(request):
    projects = Project.objects.exclude(policy="closed")
    if request.user.is_authenticated():
        projects = projects | \
            Project.objects.filter(projectmember=request.user)
    return locals()

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
def project_team_request_membership(request, project_slug):
    project = Project.objects.get(slug=project_slug)
    if not project.viewable(request):
        return HttpResponseForbidden()
    if request.user.is_anonymous():
        return HttpResponseForbidden()

    if project.has_member(request.user):
        messages.error(request, "You are already a member of this project.")
        return redirect(project)

    if request.method == "GET":
        return locals()

    prequest, created = ProjectRequest.objects.get_or_create(user=request.user, project=project)
    if not created:
        messages.info(request, "You already have a request filed.")
        return redirect(project)

    prequest.send(request.POST.get("message"))
    messages.success(request, "Good luck with your request!")
    return redirect(project)
    
@allow_http("POST")
def project_team_invite(request, project_slug):
    project = Project.objects.get(slug=project_slug)
    if not project.viewable(request):
        return HttpResponseForbidden()
    if not project.manageable(request):
        return HttpResponseForbidden()

    username = request.POST['username']
    user = User.objects.get(username=username)

    if request.POST.get("action") == "remove":
        try:
            invite = ProjectInvite.objects.get(user=user, project=project)
        except ProjectInvite.DoesNotExist:
            messages.warn(request, "No invitation to remove!")
            return redirect(project)
        invite.delete()
        messages.info(request, "The invitation has been retracted.")
        return redirect(project)

    if project.has_member(user):
        messages.error(request, "That guy is already a member of this project.")
        return redirect(project)

    try:
        invite = ProjectInvite.objects.get(user=user, project=project)
    except ProjectInvite.DoesNotExist:
        invite = ProjectInvite.objects.create(user=user, project=project,
                                              inviter=request.user)
    else:
        invite.remind(request.POST.get("message"))
        messages.info(request,
                      "A reminder has been sent to %s" % user.username)
        return redirect(project)
    invite.send(request.POST.get("message"))
    messages.success(request,
                     "An invitation has been sent to %s" % user.username)
    return redirect(project)

@allow_http("GET", "POST")
@rendered_with("opencore/project_team_manage.html")
def project_team_manage(request, project_slug):
    project = Project.objects.get(slug=project_slug)
    if not project.viewable(request):
        return HttpResponseForbidden()
    if not project.manageable(request):
        return HttpResponseForbidden()

    if request.method == "GET":
        invites = ProjectInvite.objects.filter(
            project=project)
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
