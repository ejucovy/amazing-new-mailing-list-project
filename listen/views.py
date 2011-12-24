from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import (HttpResponse,
                         HttpResponseForbidden, 
                         HttpResponseNotFound)
from django.shortcuts import redirect 
from djangohelpers import (rendered_with,
                           allow_http)
from listen.models import (
    MailingList,
    MailingListPost,
    LocalRoles,
    RolePermissions,
    SubscriptionQueue,
    PERMISSIONS,
    )
from listen.policies import get_subscription_policies, get_post_policies

@allow_http("GET", "POST")
@rendered_with("main/index_of_mailing_lists.html")
def index_of_mailing_lists(request, project_slug):
    if request.method == "GET":
        lists = MailingList.objects.all()

        member_permissions = [(-1, "not even see this list"),
                              (0, ("see the list, and its archives if they're not private; "
                                   "and request subscription; and attempt to post messages")),
                              (1, "and moderate queued posts"),
                              (2, "and moderate queued subscription requests"),
                              (3, "and add allowed senders"),
                              (4, "and edit the list's settings"),
                              ]
        other_permissions = [(-1, "not even see this list"),
                             (0, ("see the list, and its archives if they're not private; "
                                  "and request subscription; and attempt to post messages")),
                             (1, "and moderate queued posts"),
                             (2, "and moderate queued subscription requests"),
                             (3, "and add allowed senders"),
                             (4, "and edit the list's settings"),
                             ]
        subscription_policies = get_subscription_policies()
        post_policies = get_post_policies()

        return locals()

    permissions_map = ['LIST_VIEW', 'LIST_POST_MODERATE', 'LIST_SUBSCRIBE_MODERATE',
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
    post_moderation_policy = request.POST.get('post_moderation_policy')
    subscription_moderation_policy = request.POST.get('subscription_moderation_policy')

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

        created, post, message_level, message = list.submit_post(
            request.user, request.POST['subject'], request.POST['body'])

        messages.add_message(request, message_level, message)
        if created and post:            
            return redirect(post)
        else:
            return redirect(list)

    posts = MailingListPost.objects.filter(list=list, flagged=False)
    return locals()

@allow_http("POST")
def mailing_list_moderate_subscriber(request, project_slug, list_slug, subscriber_id):
    list = MailingList.objects.get(slug=list_slug)
    permissions = list.get_permissions(request.user)

    if "LIST_SUBSCRIBE_MODERATE" not in permissions:
        return HttpResponseForbidden()

    can_add_allowed_senders = ("LIST_ADD_ALLOWED_SENDERS" in permissions)

    action = request.POST['action']
    add_allowed_sender = request.POST.get('add_allowed_sender', False)
    
    queued_subscriber = SubscriptionQueue.objects.get(list=list, id=subscriber_id)
    if action == "reject":
        queued_subscriber.delete()
        return redirect(list)
    elif action == "accept":
        user_roles, _ =  LocalRoles.objects.get_or_create(
            username=queued_subscriber.user.username, list=list)
        user_roles.add_role("ListSubscriber")

        if can_add_allowed_senders and add_allowed_sender:
            user_roles.add_role("ListAllowedSender")

        user_roles.save()
        queued_subscriber.delete()
        return redirect(list)

@allow_http("GET")
def mailing_list_view_post(request, project_slug, list_slug, post_id):
    list = MailingList.objects.get(slug=list_slug)
    permissions = list.get_permissions(request.user)

    if "LIST_VIEW" not in permissions:
        return HttpResponseForbidden()

    post = MailingListPost.objects.get(list=list, id=post_id, flagged=False)
    return HttpResponse(post.body, content_type="text/plain")

@allow_http("POST")
def mailing_list_moderate_post(request, project_slug, list_slug, post_id):
    list = MailingList.objects.get(slug=list_slug)
    permissions = list.get_permissions(request.user)

    if "LIST_POST_MODERATE" not in permissions:
        return HttpResponseForbidden()

    can_add_allowed_senders = ("LIST_ADD_ALLOWED_SENDERS" in permissions)

    action = request.POST['action']
    add_allowed_sender = request.POST.get('add_allowed_sender', False)
    
    post = MailingListPost.objects.get(list=list, pk=post_id, flagged=True)
    if action == "reject":
        post.delete()
        return redirect(".")
    elif action == "accept":
        post.unflag()

        if can_add_allowed_senders and add_allowed_sender:
            user_roles, _ = LocalRoles.objects.get_or_create(
                username=post.author.username, list=list)
            user_roles.add_role("ListAllowedSender")
            user_roles.save()
        return redirect(list)

@allow_http("GET", "POST")
@rendered_with("main/mailing_list_moderate.html")
def mailing_list_moderate(request, project_slug, list_slug):
    list = MailingList.objects.get(slug=list_slug)
    permissions = list.get_permissions(request.user)

    if "LIST_POST_MODERATE" not in permissions and "LIST_SUBSCRIBE_MODERATE" not in permissions:
        return HttpResponseForbidden()

    can_add_allowed_senders = ("LIST_ADD_ALLOWED_SENDERS" in permissions)
    post_moderate = "LIST_POST_MODERATE" in permissions
    subscribe_moderate = "LIST_SUBSCRIBE_MODERATE" in permissions

    if request.method == "GET":
        queued_posts = MailingListPost.objects.filter(list=list, flagged=True) \
            if post_moderate else []
        queued_subscribers = SubscriptionQueue.objects.filter(list=list) \
            if subscribe_moderate else []
        return locals()

    action = request.POST['action']
    post_id = request.POST['post']
    add_allowed_sender = request.POST.get('add_allowed_sender', False)

@csrf_exempt
@allow_http("GET", "POST")
@rendered_with("main/request_subscription.html")
def request_subscription(request, project_slug, list_slug):
    list = MailingList.objects.get(slug=list_slug)
    permissions = list.get_permissions(request.user)

    if "LIST_VIEW" not in permissions:
        return HttpResponseForbidden()
    if request.user.is_anonymous():
        return HttpResponseForbidden()

    if request.method == "GET":
        return locals()

    success, queue, message_level, message = list.submit_subscription_request(request.user)
    messages.add_message(request, message_level, message)

    return redirect(list)


@csrf_exempt
@allow_http("GET", "POST")
@rendered_with("main/unsubscribe.html")
def unsubscribe(request, project_slug, list_slug):
    list = MailingList.objects.get(slug=list_slug)
    permissions = list.get_permissions(request.user)

    if "LIST_VIEW" not in permissions:
        return HttpResponseForbidden()
    if request.user.is_anonymous():
        return HttpResponseForbidden()

    if request.method == "GET":
        return locals()

    user_roles, _ = LocalRoles.objects.get_or_create(
        username=request.user, list=list)
    user_roles.remove_role("ListSubscriber")

    messages.success(request, "Now you are not subscribed to this list.")
    return redirect(list)
