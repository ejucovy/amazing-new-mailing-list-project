##

from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from registration.backends import get_backend
from registration.models import RegistrationProfile

from djangohelpers import rendered_with

from registration.forms import RegistrationForm

from django.contrib import messages

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
        if request.method == "GET":
            ctx = {'profile': profile, 'user': user}
            registration_form = RegistrationForm(
                initial={'email': user.email})
            ctx['registration_form'] = registration_form
            return ctx
        registration_form = RegistrationForm(data=request.POST)
        if not registration_form.is_valid():
            ctx = {'profile': profile, 'user': user}
            ctx['registration_form'] = registration_form
            return ctx
        user.username = registration_form.cleaned_data['username']
        user.set_password(registration_form.cleaned_data['password1'])
        user.save()
        messages.success(request, "You're now a real user!")

        from django.contrib.auth import authenticate
        from django.contrib.auth import login
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
