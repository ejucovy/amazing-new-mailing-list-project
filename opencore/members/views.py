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

def member_account(request, username):
    pass

def member_profile(request, username):
    pass

def member_profile_edit(request, username):
    pass

