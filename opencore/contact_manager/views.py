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
from opencore.contact_manager.models import RegistrationProfile


@allow_http("GET")
@rendered_with("contact_manager/confirm_email_contact.html")
def confirm_secondary_email_contact(request, activation_key):
    contact = RegistrationProfile.objects.confirm_contact(activation_key)
    if not contact:
        return locals()

    messages.success(request, "Your contact has been confirmed!")
    return redirect("member_account", contact.user.username)
