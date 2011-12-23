from django.conf import settings
import libopencore.auth
from httplib2 import Http
import urllib

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
    body = get_payload(msg)

    list = msg['to'].split("@")[0]
    command = None
    if '+' in list:
        list, command = list.split("+")
        command = command.lower()

    if command == "subscribe":
        payload = dict()
        url = "%s/projects/fleem/lists/%s/subscribe/" % (
            settings.SITE_DOMAIN, list)
    elif command == "unsubscribe":
        payload = dict()
        url = "%s/projects/fleem/lists/%s/unsubscribe/" % (
            settings.SITE_DOMAIN, list)
    else:
        payload = dict(body=body, subject=subject, author=contact.user.username)
        url = "%s/projects/fleem/lists/%s/" % (
            settings.SITE_DOMAIN, list)

    print headers
    resp, content = http.request(url, "POST", headers=headers, 
                                 body=urllib.urlencode(payload))
    return resp, content
