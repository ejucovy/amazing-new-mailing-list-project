from email.utils import parseaddr
from email.header import decode_header

from django.conf import settings
import libopencore.auth
from httplib2 import Http
import urllib
from listen.models import MailingList

def get_payload(msg):
    best_choice = None
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get_content_type() == 'text/html':
            best_choice = part
            break
        if best_choice is None and part.get_content_type() == 'text/plain':
            best_choice = part
    if best_choice is None:
        # No text/plain or text/html message was found in the email
        # so we'll just reject it for now.
        # TODO: figure out a sane approach to email content-type handling
        return None
    # TODO: process text/html message differently
    charset = (best_choice.get_content_charset() or best_choice.get_charset()
               or msg.get_content_charset() or msg.get_charset()
               or 'utf-8')
    return best_choice.get_payload(decode=True).decode(charset)

def email_to_http(msg, contact):
    http = Http()
    headers = {}

    secret = libopencore.auth.get_secret(settings.OPENCORE_SECRET_FILENAME)
    val = libopencore.auth.generate_cookie_value(
        contact.user.username, secret)
    
    headers['Cookie'] = "__ac=%s" % val

    subject = msg['subject']
    subject = decode_header(subject)

    body = get_payload(msg)

    ### XXX TODO: componentization of this list-locating logic?
    addr = msg['To']
    addr = parseaddr(addr)[1]
    list = addr.split("@")[0]
    command = None
    if '+' in list:
        list, command = list.split("+")
        command = command.lower()
    list = MailingList.objects.get(slug=list)
    project = list.container_id
    assert project and project.endswith(".projects")
    project = project[:-len(".projects")]

    if command == "subscribe":
        payload = dict()
        url = "http://%s/projects/%s/lists/%s/subscribe/" % (
            settings.SITE_DOMAIN, project, list)
    elif command == "unsubscribe":
        payload = dict()
        url = "http://%s/projects/%s/lists/%s/unsubscribe/" % (
            settings.SITE_DOMAIN, project, list)
    else:
        payload = dict(body=body, subject=subject, 
                       author=contact.user.username)
        url = "http://%s/projects/%s/lists/%s/" % (
            settings.SITE_DOMAIN, project, list)

    print headers
    resp, content = http.request(url, "POST", headers=headers, 
                                 body=urllib.urlencode(payload))
    print resp, content
    return resp, content
