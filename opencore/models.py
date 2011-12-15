from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
import libopencore.auth

def set_cookie(sender, request, user, **kwargs):
    secret = libopencore.auth.get_secret(settings.OPENCORE_SECRET_FILENAME)
    val = libopencore.auth.generate_cookie_value(user.username, secret)
    request.set_cookie("__ac", val)
user_logged_in.connect(set_cookie)

def unset_cookie(sender, request, user, **kwargs):
    request.delete_cookie("__ac")
user_logged_out.connect(unset_cookie)
