
from django.contrib.auth.models import User
def display_name(self):
    display_name = self.get_full_name() or User.__original_unicode__(self)
    if self.is_active:
        return display_name
    if self.has_usable_password():
        return u"%s (unconfirmed account)" % display_name
    return u"%s...%s (unconfirmed account)" % (
        self.email[:3], self.email.split("@")[-1])
User.__original_unicode__ = User.__unicode__
User.__unicode__ = display_name
