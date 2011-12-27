from django.conf import settings
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from registration.backends import get_backend
from registration.models import RegistrationProfile

from djangohelpers import rendered_with, allow_http

from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm

from django.contrib import messages

from main.email import EmailMessageWithEnvelopeTo
from main.models import EmailContact
from opencore.models import ProjectInvite
from opencore.registration_workflow.forms import RegistrationForm

@rendered_with("opencore/member/account_first_time.html")
def activate(request, activation_key, 
             backend,
             template_name='registration/activate.html',
             success_url=None, extra_context=None, **kwargs):

    force_rename = False
    try:
        profile = RegistrationProfile.objects.get(
            activation_key=activation_key)
    except RegistrationProfile.DoesNotExist:
        pass
    else:
        if ( not profile.activation_key_expired()
             and not profile.user.has_usable_password() ):
            force_rename = True
    
    if force_rename is True:
        user = profile.user
        confirmed_email = profile.user.email

        if request.method == "GET":
            ctx = {'profile': profile, 'user': user}
            registration_form = RegistrationForm(
                initial={'email': confirmed_email})
            login_form = AuthenticationForm()
            ctx['registration_form'] = registration_form
            ctx['login_form'] = login_form
            return ctx
        
        if request.POST.get("claim_account") == "true":
            login_form = AuthenticationForm(data=request.POST)
            if not login_form.is_valid():
                ctx = {'profile': profile, 'user': user}
                ctx['registration_form'] = RegistrationForm(
                    initial={'email': confirmed_email})
                ctx['login_form'] = login_form
                return ctx
            claimed_user = login_form.get_user()
            original_user = user
            ProjectInvite.objects.filter(user=original_user).update(
                user=claimed_user)
            EmailContact.objects.filter(user=original_user).update(
                user=claimed_user)
            login(request, claimed_user)
            if claimed_user.is_active:
                contact, _ = EmailContact.objects.get_or_create(
                    user=claimed_user, email=confirmed_email)
                contact.confirm()

            profile.delete()
            messages.success(request, "You've claimed this email address.")
            backend = get_backend(backend)
            to, args, kwargs = backend.post_activation_redirect(
                request, claimed_user)
            if success_url is None:
                return redirect(to, *args, **kwargs)
            else:
                return redirect(success_url)

        else:
            registration_form = RegistrationForm(data=request.POST)
            if not registration_form.is_valid():
                ctx = {'profile': profile, 'user': user}
                ctx['registration_form'] = registration_form
                ctx['login_form'] = AuthenticationForm()
                return ctx
            user.username = registration_form.cleaned_data['username']
            user.set_password(registration_form.cleaned_data['password1'])
            user.save()
            messages.success(request, "You're now a real user!")

            user_with_backend = authenticate(
                username=user.username, 
                password=registration_form.cleaned_data['password1'])
            login(request, user_with_backend)

    backend = get_backend(backend)
    account = backend.activate(request, activation_key)

    if account and account.has_usable_password():
        if success_url is None:
            to, args, kwargs = backend.post_activation_redirect(request, account)
            return redirect(to, *args, **kwargs)
        else:
            return redirect(success_url)

    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value

    context['activation_key'] = activation_key

    return render_to_response(template_name,
                              kwargs,
                              context_instance=context)

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
