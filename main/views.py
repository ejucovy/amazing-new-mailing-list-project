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

@csrf_exempt
@allow_http("GET", "POST")
@rendered_with("main/mailing_list.html")
def mailing_list(request, project_slug, list_slug):
    list = MailingList.objects.get(slug=list_slug)
    if request.method == "POST":

        post = MailingListPost.objects.create(
            list=list,
            author=request.user,
            subject=request.POST['subject'],
            body=request.POST['body'])
        post.save()
        return redirect(".")

    return locals()
