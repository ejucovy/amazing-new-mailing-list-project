from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect

from djangohelpers import rendered_with, allow_http

from main.mail import EmailMessageWithEnvelopeTo
from main.models import EmailContact
from opencore.models import ProjectInvite
from opencore.registration_workflow.forms import RegistrationForm

@allow_http("GET", "POST")
@rendered_with("registration/registration_form.html")
def register(request):
    form = RegistrationForm()

    if request.method == "GET":
        return locals()

    form = RegistrationForm(request.POST)    
    if not form.is_valid():
        return locals()

    new_user = form.save()
    registration_profile = form.profile

    subject = "Please confirm your email address"
    body = registration_profile.render_to_string(
        "contact_manager/confirm_initial_email_contact.txt")
    email = EmailMessageWithEnvelopeTo(subject, body,
                                       settings.DEFAULT_FROM_EMAIL,
                                       [registration_profile.contact.email])
    email.send()

    new_user = authenticate(username=new_user.username, password=form.cleaned_data['password1'])
    login(request, new_user)

    messages.success(request, "Now check your email to activate your account.")
    return redirect("member_account", new_user.username)
