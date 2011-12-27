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
from main.models import EmailContact
from opencore.contact_manager.forms import EmailContactForm
from main.mail import EmailMessageWithEnvelopeTo

@allow_http("GET")
@rendered_with("opencore/member/index_of_members.html")
def index_of_members(request):
    users = User.objects.filter(is_active=True)
    return locals()

def member_home(request, username):
    return redirect("member_profile", username)

@allow_http("GET")
@rendered_with("opencore/member/account.html")
def member_account(request, username):
    user = User.objects.get(username=username)
    if user != request.user:
        return HttpResponseForbidden()
    invites = ProjectInvite.objects.filter(user=user)

    memberships = ProjectMember.objects.filter(user=user)
    contacts = EmailContact.objects.filter(user=user)

    contact_add_form = EmailContactForm()

    return locals()

@allow_http("POST")
@rendered_with("opencore/member/account.html")
def member_email_contacts(request, username):
    user = User.objects.get(username=username)
    if user != request.user:
        return HttpResponseForbidden()

    contact_add_form = EmailContactForm(data=request.POST)
    if not contact_add_form.is_valid():
        return locals()
    
    new_contact = contact_add_form.save(user)
    registration_profile = contact_add_form.profile
    subject = "Please confirm your email address"
    body = registration_profile.render_to_string(
        "contact_manager/confirm_secondary_email_contact.txt")
    email = EmailMessageWithEnvelopeTo(subject, body, 
                                       settings.DEFAULT_FROM_EMAIL,
                                       [new_contact.email])
    email.send()

    messages.info(request, "Now check your email to confirm the contact.")
    return redirect("member_account", user.username)

@allow_http("POST")
@rendered_with("opencore/member/account.html")
def member_email_contacts_entry(request, username, contact_id):
    user = User.objects.get(username=username)
    if user != request.user:
        return HttpResponseForbidden()
    contact = EmailContact.objects.get(user=user, id=contact_id, 
                                       confirmed=True)
    user.email = contact.email
    user.save()

    messages.success(request,
                     "Your primary email contact is now %s" % user.email)
    return redirect("member_account", user.username)

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
        return redirect("member_account", user.username)

    invites.delete()
    if request.POST['action'] == 'reject':
        return redirect("member_account", user.username)
    
    assert request.POST['action'] == 'accept'
    if ProjectMember.objects.filter(
        user=user, project=project).count() > 0:
        messages.info(
            request, 
            "You are already a member of this project.")
        return redirect("member_account", user.username)
        
    membership = ProjectMember(user=user, project=project,
                               role="ProjectMember")
    membership.save()
    messages.success(request, "Poof!  You're a member.")
    return redirect("member_account", user.username)

@allow_http("GET")
@rendered_with("opencore/member/profile.html")
def member_profile(request, username):
    user = User.objects.get(username=username, is_active=True)
    return locals()

def member_profile_edit(request, username):
    pass

