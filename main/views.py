from django.views.decorators.csrf import csrf_exempt
from django.http import (HttpResponse,
                         HttpResponseForbidden, 
                         HttpResponseNotFound)
from django.shortcuts import redirect 
from djangohelpers import (rendered_with,
                           allow_http)
from main.models import *

@allow_http("GET")
@rendered_with("main/home.html")
def home(request):
    return {}

@allow_http("GET", "POST")
@rendered_with("main/index_of_mailing_lists.html")
def index_of_mailing_lists(request, project_slug):
    if request.method == "GET":
        lists = MailingList.objects.all()
        return locals()

    slug = request.POST['slug']
    list = MailingList.objects.create(slug=slug)
    list.save()

    member_permissions = (
        "LIST_VIEW",
        )
    authenticated_permissions = (
        "LIST_VIEW",
        )
    anonymous_permissions = (
        "LIST_VIEW",
        )
    allowed_sender_permissions = (
        "LIST_POST",
        )
    subscriber_permissions = (
        )

    p = RolePermissions(list=list, role="ProjectMember")
    p.set_permissions(member_permissions)
    p.save()

    p = RolePermissions(list=list, role="Authenticated")
    p.set_permissions(authenticated_permissions)
    p.save()

    p = RolePermissions(list=list, role="Anonymous")
    p.set_permissions(anonymous_permissions)
    p.save()

    p = RolePermissions(list=list, role="ListAllowedSender")
    p.set_permissions(allowed_sender_permissions)
    p.save()

    p = RolePermissions(list=list, role="ListSubscriber")
    p.set_permissions(subscriber_permissions)
    p.save()
    
    return redirect(".")

@csrf_exempt
@allow_http("GET", "POST")
@rendered_with("main/mailing_list.html")
def mailing_list(request, project_slug, list_slug):
    list = MailingList.objects.get(slug=list_slug)
    if request.method == "POST":

        post = list.submit_post(request.user, 
                                request.POST['subject'], 
                                request.POST['body'])
        return redirect(".")

    posts = MailingListPost.objects.filter(list=list, flagged=False)
    return locals()

@allow_http("GET", "POST")
@rendered_with("main/mailing_list_moderate.html")
def mailing_list_moderate(request, project_slug, list_slug):
    list = MailingList.objects.get(slug=list_slug)
    permissions = list.get_permissions(request.user)

    if "LIST_POST_MODERATE" not in permissions:
        return HttpResponseForbidden()

    can_moderate_users = ("LIST_ADD_ALLOWED_SENDERS" in permissions)
    
    if request.method == "GET":
        queued_posts = MailingListPost.objects.filter(list=list, flagged=True)
        return locals()

    action = request.POST['action']
    post_id = request.POST['post']
    add_allowed_sender = request.POST.get('add_allowed_sender', False)

    post = MailingListPost.objects.get(list=list, pk=post_id, flagged=True)
    if action == "reject":
        post.delete()
        return redirect(".")
    elif action == "accept":
        post.unflag()

        if can_moderate_users and add_allowed_sender:
            user_roles, _ = LocalRoles.objects.get_or_create(
                username=post.author.username, list=list)
            user_roles.add_role("ListAllowedSender")
            user_roles.save()
        return redirect(".")
