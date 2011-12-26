
from django.contrib.auth.models import User
def display_name(self):
    if self.is_active:
        return self.get_full_name() or User.__original_unicode__(self)
    return u"%s...%s (unconfirmed account)" % (
        self.email[:3], self.email.split("@")[-1])
User.__original_unicode__ = User.__unicode__
User.__unicode__ = display_name


from registration.backends.default import DefaultBackend
from django.contrib import messages
def post_activation_redirect(self, request, user):
    """
    Return the name of the URL to redirect to after successful
    account activation.
    """

    if user.has_usable_password():
        messages.success(request, "Congratulations!  Welcome.")
        return ('member_account', (user.username), {})

    messages.success(request, "Welcome!  Please choose a username and password for your account.")
    return ('member_account_first_time', [user.username], {})

DefaultBackend.post_activation_redirect = post_activation_redirect
