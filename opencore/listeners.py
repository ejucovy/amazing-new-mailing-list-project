import email
from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
import libopencore.auth
from registration.signals import user_registered, user_activated
from opencore.signals import contact_confirmed
from main.models import EmailContact, DeferredMessage
from main import gateway
from django.contrib.auth import login
from django.contrib.auth import authenticate

def set_cookie(sender, request, user, **kwargs):
    secret = libopencore.auth.get_secret(settings.OPENCORE_SECRET_FILENAME)
    val = libopencore.auth.generate_cookie_value(user.username, secret)
    request.set_cookie("__ac", val)
user_logged_in.connect(set_cookie)

def unset_cookie(sender, request, user, **kwargs):
    request.delete_cookie("__ac")
user_logged_out.connect(unset_cookie)

def confirm_email_contact(sender, user, **kwargs):
    if not user.is_active:
        return False
    email = user.email
    contact, _ = EmailContact.objects.get_or_create(email=email, user=user)
    contact.confirm()
user_activated.connect(confirm_email_contact)

def process_deferrals(sender, contact, **kwargs):
    if not contact.confirmed:
        return False
    if not contact.user.is_active:
        return False
    deferrals = DeferredMessage.objects.filter(contact=contact)
    for deferral in deferrals:
        message = deferral.message.encode("utf-8")
        msg = email.message_from_string(message)
        gateway.process(msg)
        deferral.delete()
contact_confirmed.connect(process_deferrals)

def log_in_user(sender, user, request, **kwargs):
    user_with_backend = authenticate(username=user.username,
                                     password=request.POST['password1'])
    login(request, user_with_backend)
user_registered.connect(log_in_user)
