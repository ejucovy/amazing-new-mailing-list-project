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
    registration_form = PresetEmailRegistrationForm(email=contact.email)
    if request.method == "GET":
        return locals()

    if request.POST.get("delete") == "true":
        profile.delete()
        contact.delete()
        messages.info(request, "Okay, the contact has been deleted.")
        return redirect("home")

    if request.POST.get("register") == "true":
        registration_form = PresetEmailRegistrationForm(email=contact.email, data=request.POST)
        if not registration_form.is_valid():
            return locals()
        new_user = User.objects.create_user(registration_form.cleaned_data['username'],
                                            contact.email,
                                            registration_form.cleaned_data['password1'])
        contact.user = new_user
        contact.save()
        
        new_user = authenticate(username=registration_form.cleaned_data['username'],
                                password=registration_form.cleaned_data['password1'])
        login(request, new_user)

        profile.confirm_contact()

        new_user.is_active = True
        new_user.save()

        messages.success(
            request,
            "Your contact has been confirmed and you have created a new account %s" % new_user)
        return redirect("member_account", new_user.username)


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
