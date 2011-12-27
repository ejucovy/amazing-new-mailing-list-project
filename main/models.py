from django.db import models

from opencore.signals import contact_confirmed

class EmailContact(models.Model):
    email = models.EmailField(unique=True)
    confirmed = models.BooleanField(default=False)
    user = models.ForeignKey("auth.user")
    
    def __unicode__(self):
        return "Email %s for user %s (%sconfirmed)" % (
            self.email, self.user, "" if self.confirmed else "not ")

    def confirm(self):
        if self.confirmed:
            return False
        self.confirmed = True
        self.save()
        contact_confirmed.send(sender=self.__class__, contact=self)
        return True

class DeferredMessage(models.Model):
    contact = models.ForeignKey(EmailContact)
    message = models.TextField()
    deferred_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "Deferred message attached to %s:\n%s" % (
            self.contact, self.message)
