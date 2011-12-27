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
from main.models import EmailContact

import random
from django.conf import settings
from django.template.loader import render_to_string
from registration.models import RegistrationProfile

def random_name():
    return "".join(random.choice("abcdefghijklmnopqrxtuvwxyz"
                                 "ABCDEFGHIJKLMNOPQRXTUVWXYZ"
                                 "1234567890@.+-_") for i in range(30))

@allow_http("GET")
@rendered_with("base.html")
def theme(request):
    return locals()

@allow_http("GET", "POST")
@rendered_with("opencore/index_of_projects.html")
def index_of_projects(request):
    projects = Project.objects.exclude(policy="policy_closed")
    if request.user.is_authenticated():
        projects = projects | \
            Project.objects.filter(projectmember=request.user)
    projects = projects.distinct()
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
def project_team_invite_email(request, project_slug):
    project = Project.objects.get(slug=project_slug)
    if not project.viewable(request):
        return HttpResponseForbidden()
    if not project.manageable(request):
        return HttpResponseForbidden()

    email = request.POST['email']
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        pass
    else:
        messages.info(request, "This user already exists. Search better.")
        return redirect(project)

    user = RegistrationProfile.objects.create_inactive_user(
        username=random_name(), password=random_name(), email=email, 
        site=None, send_email=False)
    user.is_active = False
    user.set_unusable_password()
    user.save()

    contact = EmailContact.objects.create(
        email=email, confirmed=False, user=user)
    contact.save()

    invite = ProjectInvite.objects.create(user=user, project=project,
                                          inviter=request.user)

    registration_profile = RegistrationProfile.objects.get(user=user)
    ctx_dict = {'activation_key': registration_profile.activation_key,
                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                'site': {'domain': settings.SITE_DOMAIN,
                         'name': settings.SITE_NAME},
                }

    ctx_dict['invite'] = invite
    custom_message = request.POST.get('custom_message') or ''
    if custom_message and custom_message.strip():
        ctx_dict['custom_message'] = custom_message.strip()

    subject = "You're been invited"
    message = render_to_string(
        'gateway/project_invite_pending_activation_email.txt', ctx_dict)
    email = EmailMessageWithEnvelopeTo(subject, message, 
                                       settings.DEFAULT_FROM_EMAIL,
                                       [contact.email])
    email.send()

    messages.success(request, "Your invitation has been sent.")
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

        if ( 'invite_search' in request.GET
             and request.GET['invite_search'] is not None
             and request.GET['invite_search'].strip() ):
            invite_search = request.GET['invite_search'].strip()
            invite_search_results = ( User.objects.filter(
                    username__icontains=invite_search) |
                                      User.objects.filter(
                    email__icontains=invite_search) |
                                      User.objects.filter(
                    first_name__icontains=invite_search) |
                                      User.objects.filter(
                    last_name__icontains=invite_search) 
                                      )
            invite_search_results = invite_search_results.exclude(
                projectinvite__project=project).exclude(
                projectmember__project=project)

        return locals()

    form = TeamForm(project, data=request.POST)
    if not form.is_valid():
        return locals()
    memberships = form.save()
    messages.success(request, "Modified %s memberships" % len(memberships))
    return redirect(project)

@csrf_exempt
@allow_http("GET", "POST")
@rendered_with("opencore/project_info.xml")
def project_info(request, project_slug):
    project = Project.objects.get(slug=project_slug)
    if not project.viewable(request):
        return HttpResponseForbidden()
    return locals()

@csrf_exempt
@allow_http("GET", "POST")
@rendered_with("opencore/project_info_members.xml")
def project_info_members(request, project_slug):
    project = Project.objects.get(slug=project_slug)
    if not project.viewable(request):
        return HttpResponseForbidden()
    return locals()
