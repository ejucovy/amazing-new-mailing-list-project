from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
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

        member_permissions = [(-1, "not even see this list"),
                              (0, ("see the list, and its archives if they're not private; "
                                   "and request subscription; and attempt to post messages")),
                              (1, "and moderate queued posts"),
                              (2, "and add allowed senders"),
                              (3, "and edit the list's settings"),
                              ]
        other_permissions = [(-1, "not even see this list"),
                             (0, ("see the list, and its archives if they're not private; "
                                  "and request subscription; and attempt to post messages")),
                             (1, "and moderate queued posts"),
                             (2, "and add allowed senders"),
                             (3, "and edit the list's settings"),
                             ]

        return locals()

    permissions_map = ['LIST_VIEW', 'LIST_POST_MODERATE',
                       'LIST_ADD_ALLOWED_SENDERS', 'LIST_CONFIGURE']

    slug = request.POST['slug']
    list = MailingList.objects.create(slug=slug)
    list.save()

    member_perms = int(request.POST.get('member_perms', -1))
    member_permissions = permissions_map[:member_perms + 1]

    other_perms = int(request.POST.get('other_perms', -1))
    authenticated_permissions = permissions_map[:other_perms + 1]

    anonymous_permissions = ('LIST_VIEW',) if 'LIST_VIEW' in authenticated_permissions else ()

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

    archive_attachments = 'archive_attachments' in request.POST
    archive_messages = 'archive_messages' in request.POST
    private_archives = 'private_archives' in request.POST
    post_moderation_policy = 'post_moderation_policy' in request.POST
    subscription_moderation_policy = 'subscription_moderation_policy' in request.POST

    list.set_options(dict(
            archive_attachments=archive_attachments,
            archive_messages=archive_messages,
            private_archives=private_archives,
            post_moderation_policy=post_moderation_policy,
            subscription_moderation_policy=subscription_moderation_policy,
            ))
    list.save()
    
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
        queued_subscribers = SubscriptionQueue.objects.filter(list=list)
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

@csrf_exempt
@allow_http("GET", "POST")
@rendered_with("main/request_subscription.html")
def request_subscription(request, project_slug, list_slug):
    list = MailingList.objects.get(slug=list_slug)
    permissions = list.get_permissions(request.user)

    if "LIST_VIEW" not in permissions or request.user.is_anonymous():
        return HttpResponseForbidden()

    if request.method == "GET":
        return locals()

    user_roles, _ = LocalRoles.objects.get_or_create(
        username=request.user.username, list=list)

    if list.subscription_moderation_policy:
        queue, _ = SubscriptionQueue.objects.get_or_create(
            user=request.user,
            list=list,
            )
        queue.save()
        messages.info(request, 
                      "Your request for moderation has been submitted to senior management")
    else:
        user_roles.add_role('ListSubscriber')
        messages.success(request,
                         "Congratulations, you're now subscribed.")

    return redirect('..')
