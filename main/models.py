from django.db import models

class EmailContact(models.Model):
    email = models.EmailField()
    confirmed = models.BooleanField(default=False)
    user = models.ForeignKey("auth.user")

    def __unicode__(self):
        return "Email %s for user %s (%sconfirmed)" % (
            self.email, self.user, "" if self.confirmed else "not ")

class DeferredMessage(models.Model):
    contact = models.ForeignKey(EmailContact)
    message = models.TextField()
    deferred_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "Deferred message attached to %s:\n%s" % (
            self.contact, self.message)

class MailingList(models.Model):
    slug = models.CharField(max_length=100, unique=True)
    
    @property
    def private_archives(self):
        return False

    @property
    def archive_messages(self):
        return True

    @property
    def archive_attachments(self):
        return False

    @property
    def posting_policy(self):
        return "Fleem"

class AllowedSender(models.Model):
    list = models.ForeignKey(MailingList)
    user = models.ForeignKey("auth.user")

class MailingListPost(models.Model):
    author = models.ForeignKey("auth.user")
    list = models.ForeignKey(MailingList)
    created = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=100)
    body = models.TextField()

    
