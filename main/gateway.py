from email.utils import parseaddr
from email.header import decode_header

from celery.task import task
from django.conf import settings
from django.contrib.auth.models import User
from zope.dottedname.resolve import resolve

from main.email import EmailMessageWithEnvelopeTo
from main.models import EmailContact, DeferredMessage
from opencore.registration_workflow.forms import TemporaryAccountFactory

def process(msg):
    addr = msg.get("From")
    addr = parseaddr(addr)[1]

    try:
        contact = EmailContact.objects.get(email=addr)
    except EmailContact.DoesNotExist:
        return new_contact(msg)

    if not contact.confirmed:
        return defer(msg, contact)

    return convert_to_web(msg, contact)

def new_contact(msg):
    email = msg.get("From")
    addr = parseaddr(addr)[1]

    factory = TemporaryAccountFactory(email)
    registration_form = factory.registration_form()
    new_user = factory.create_temporary_user(registration_form)

    registration_profile = registration_form.profile
    contact = registration_form.contact

    subject = "Please confirm your account"
    message = registration_profile.render_to_string(
        'gateway/listen_mail_pending_activation_email.txt')
    email = EmailMessageWithEnvelopeTo(subject, message, 
                                       settings.DEFAULT_FROM_EMAIL,
                                       [contact.email])
    email.send()

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

