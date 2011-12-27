from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import (HttpResponse,
                         HttpResponseForbidden, 
                         HttpResponseNotFound)
from django.shortcuts import redirect 
from django.views.decorators.csrf import csrf_exempt

from djangohelpers import (rendered_with,
                           allow_http)

from registration.forms import RegistrationForm

from opencore.models import *
from main.models import EmailContact
from opencore.contact_manager.models import RegistrationProfile

class PresetEmailRegistrationForm(RegistrationForm):
    email = forms.EmailField(widget=forms.HiddenInput, required=False)

    def __init__(self, email, *args, **kwargs):
        RegistrationForm.__init__(self, *args, **kwargs)
        self.preset_email = email

    def clean_email(self):
        return self.preset_email

@allow_http("GET")
def confirm_initial_email_contact(request, activation_key):
    try:
        profile = RegistrationProfile.objects.get(activation_key=activation_key)
    except RegistrationProfile.DoesNotExist:
        messages.error(request, "This link is invalid, sorry.")
        return redirect("home")
    if profile.activation_key_expired():
        messages.error(request, "This link is expired, sorry.")
        return redirect("home")

    contact = profile.contact
    user = contact.user

    if contact.confirmed:
        messages.error(request, "This contact is already confirmed.")
        ## TODO: system is in a logically inconsistent state. fix the profile object
        return redirect("home")

    if not user.has_usable_password():
        messages.error(request, "We need to redirect you to a page where you can choose a username and password.") ## XXX TODO
        return redirect("home")

    if user.is_active:
        return redirect("confirm_secondary_email_contact", activation_key)

    profile.confirm_contact()
    user.is_active = True
    user.save()

    ## TODO: process Deferred Messages

    messages.success(request, "Your account is now confirmed -- go forth and conquer!")
    return redirect("member_account", user.username)
    

@allow_http("GET", "POST")
@rendered_with("contact_manager/confirm_email_contact.html")
def confirm_secondary_email_contact(request, activation_key):
    try:
        profile = RegistrationProfile.objects.get(activation_key=activation_key)
    except RegistrationProfile.DoesNotExist:
        messages.error(request, "This link is invalid, sorry.")
        return redirect("home")
    if profile.activation_key_expired():
        messages.error(request, "This link is expired, sorry.")
        return redirect("home")

    contact = profile.contact
    user = contact.user

    if contact.confirmed:
        messages.error(request, "This contact is already confirmed.")
        ## TODO: system is in a logically inconsistent state. fix the profile object
        return redirect("home")

    if not user.has_usable_password():
        messages.error(request, "We need to redirect you to a page where you can choose a username and password.") ## XXX TODO
        return redirect("home")

    if not user.is_active:
        return redirect("confirm_initial_email_contact", activation_key)

    if request.method == "GET":
        return locals()

    login_form = AuthenticationForm(data=request.POST)
    if not login_form.is_valid():
        messages.info(request, "There was an error, please check your password and try again.")
        return redirect(".")
    claimant_user = login_form.get_user()

    ## XXX TODO
    assert claimant_user == contact.user

    login(request, claimant_user)
    profile.confirm_contact()

    ## XXX TODO
    assert claimant_user.is_active

    ## TODO: process Deferred Messages

    messages.success(
        request,
        "Your contact has been confirmed and associated with your account %s" % claimant_user)
    return redirect("member_account", claimant_user.username)
