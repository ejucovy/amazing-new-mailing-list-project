import email
from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
import libopencore.auth
from opencore.signals import user_activated, contact_confirmed
from main.models import EmailContact, DeferredMessage
from main import gateway

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
    contact.save()
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
