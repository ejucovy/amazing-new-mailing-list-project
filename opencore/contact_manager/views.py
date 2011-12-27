from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
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


@allow_http("GET", "POST")
@rendered_with("contact_manager/confirm_email_contact.html")
def confirm_secondary_email_contact(request, activation_key):
    try:
        profile = RegistrationProfile.objects.get(activation_key=activation_key)
    except RegistrationProfile.DoesNotExist:
        messages.error(request, "This link is invalid or expired, sorry.")
        return redirect("home")
    if profile.activation_key_expired():
        messages.error(request, "This link is invalid or expired, sorry.")
        return redirect("home")

    contact = profile.contact
    if request.method == "GET":
        return locals()

    if request.POST.get("delete") == "true":
        profile.delete()
        contact.delete()
        messages.info(request, "Okay, the contact has been deleted.")
        return redirect("home")

    login_form = AuthenticationForm(data=request.POST)
    if not login_form.is_valid():
        messages.info(request, "There was an error, please check your password and try again.")
        return redirect(".")
    claimant_user = login_form.get_user()
    if claimant_user != contact.user:
        contact.user = claimant_user
        contact.save()

    login(request, claimant_user)
    profile.confirm_contact()

    if not claimant_user.is_active:
        claimant_user.is_active = True
        claimant_user.save()

    messages.success(
        request,
        "Your contact has been confirmed and associated with your account %s" % claimant_user)
    return redirect("member_account", claimant_user.username)
