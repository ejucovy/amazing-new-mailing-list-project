import random
from django.conf import settings
from django.contrib.auth.models import User
from registration.models import RegistrationProfile
from zope.dottedname.resolve import resolve
from main.models import EmailContact, DeferredMessage
from celery.decorators import task

def random_name():
    return "".join(random.choice("abcdefghijklmnopqrxtuvwxyz"
                                 "ABCDEFGHIJKLMNOPQRXTUVWXYZ"
                                 "1234567890@.+-_") for i in range(30))

def process(msg):
    addr = msg.get("From")
    
    try:
        contact = EmailContact.objects.get(email=addr)
    except EmailContact.DoesNotExist:
        return new_contact(msg)

    if not contact.confirmed:
        return defer(msg, contact)

    return convert_to_web.delay(msg, contact)

def new_contact(msg):
    addr = msg.get("From")

    user = RegistrationProfile.objects.create_inactive_user(
        username=random_name(), password=random_name(), email=addr)
    user.is_active = False
    user.set_unusable_password()
    user.save()

    contact = EmailContact.objects.create(
        email=addr, confirmed=False, user=user)
    contact.save()

    return defer(msg, contact)

def defer(msg, contact):
    deferred = DeferredMessage.objects.create(contact=contact,
                                              message=msg.as_string())
    deferred.save()
    return deferred

@task()
def convert_to_web(msg, contact):
    response, content = resolve(
        getattr(settings, 'EMAIL_TO_WEB_ROUTER', 
                "main.routers.email_to_http"))(msg, contact)
    return response, content

