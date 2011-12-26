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

def index_of_members(request):
    pass

def member_home(request, username):
    pass

@allow_http("GET")
@rendered_with("opencore/member/account.html")
def member_account(request, username):
    user = User.objects.get(username=username)
    if user != request.user:
        return HttpResponseForbidden()
    invites = ProjectInvite.objects.filter(user=user)

    memberships = ProjectMember.objects.filter(user=user)
    return locals()

@allow_http("POST")
def member_project_invites(request, username, project_slug):
    user = User.objects.get(username=username)
    project = Project.objects.get(slug=project_slug)
    if user != request.user:
        return HttpResponseForbidden()

    invites = ProjectInvite.objects.filter(
        user=user, project=project)
    if len(invites) == 0:
        messages.error(
            request, "No such invitation exists.")
        return redirect("member_account", [user.username])

    invites.delete()
    if request.POST['action'] == 'reject':
        return redirect("member_account", [user.username])
    
    assert request.POST['action'] == 'accept'
    if ProjectMember.objects.filter(
        user=user, project=project).count() > 0:
        messages.info(
            request, 
            "You are already a member of this project.")
        return redirect("member_account", [user.username])
        
    membership = ProjectMember(user=user, project=project,
                               role="ProjectMembeR")
    membership.save()
    messages.success(request, "Poof!  You're a member.")
    return redirect("member_account", [user.username])

def member_profile(request, username):
    pass

def member_profile_edit(request, username):
    pass

