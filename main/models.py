from ConfigParser import RawConfigParser
from ConfigParser import NoOptionError, NoSectionError
from StringIO import StringIO

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models

from opencore.signals import contact_confirmed

class _NoDefault(object):
    def __repr__(self):
        return "(no default)"
NoDefault = _NoDefault()
del _NoDefault

class EmailContact(models.Model):
    email = models.EmailField()
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

class MailingList(models.Model):
    slug = models.CharField(max_length=100, unique=True)
    config = models.TextField(null=True, blank=True)

    def set_options(self, kwargs, section="options"):
        if not self.config:
            self.config = "[%s]" % section
        config = RawConfigParser()
        fp = StringIO(self.config)
        config.readfp(fp)

        if not config.has_section(section):
            config.add_section(section)

        for key, val in kwargs.items():
            config.set(section, key, val)

        fp = StringIO()
        config.write(fp)
        fp.seek(0)
        self.config = fp.read()
        self.save()
    
    def get_option(self, key, default=NoDefault, asbool=False, section="options"):
        config = RawConfigParser()
        fp = StringIO(self.config)
        config.readfp(fp)
        try:
            value = config.get(section, key)
        except (NoOptionError, NoSectionError):
            if default is NoDefault:
                raise
            return default

        if not asbool:
            return value.strip()

        value = value.lower()
        if value in ("1", "true", "t", "yes", "y", "on"):
            return True
        elif value in ("0", "false", "f", "no", "n", "off"):
            return False
        else:
            raise TypeError("Cannot convert to bool: %s" % value)

    @property
    def archive_messages(self):
         return self.get_option("archive_messages", asbool=True,
                                default=True)

    @property
    def archive_attachments(self):
        return self.get_option("archive_attachments", asbool=True,
                               default=False)

    @property
    def private_archives(self):
        return self.get_option("private_archives", asbool=True,
                               default=False)

    def get_permissions(self, user):
        if user.is_superuser:
            return set(i[0] for i in PERMISSIONS)

        if user.is_authenticated() and user.is_active:
            username = user.username
            user_roles = LocalRoles.objects.filter(username=username, 
                                                   list=self)
            roles = set("AUTHENTICATED")
        else:
            user_roles = []
            roles = set("ANONYMOUS")

        for user_role in user_roles:
            roles.update(user_role.get_roles())
        role_permissions = RolePermissions.objects.filter(
            list=self, role__in=roles)
        permissions = set()
        for role_permission in role_permissions:
            permissions.update(role_permission.get_permissions())
        return permissions

    def flag_post(self, author, subject, body):
        post = MailingListPost.objects.create(list=self, author=author,
                                              subject=subject, body=body,
                                              flagged=True)
        post.save()
        return post

    def submit_post(self, author, subject, body):
        permissions = self.get_permissions(author)

        if "LIST_POST" in permissions:
            post = MailingListPost.objects.create(list=self, author=author,
                                                  subject=subject, body=body)
            post.save()
            return post
        else:
            return self.flag_post(author, subject, body)

    def send_to_subscribers(self, post):
        author = post.author.email
        subject = post.subject
        body = post.body

        domain = settings.SITE_DOMAIN
        subject = ''.join(subject.splitlines())

        subscribers = LocalRoles.objects.filter(list=self, roles__contains="ListSubscriber")
        subscribers = [i.username for i in subscribers]
        subscribers = User.objects.filter(is_active=True, username__in=subscribers)
        subscribers = [i.email for i in subscribers]

        send_mail(subject, body, author, subscribers)

class AllowedSender(models.Model):
    list = models.ForeignKey(MailingList)
    user = models.ForeignKey("auth.user")

class MailingListPost(models.Model):
    author = models.ForeignKey("auth.user")
    list = models.ForeignKey(MailingList)

    flagged = models.BooleanField(default=False, db_index=True)

    created = models.DateTimeField(auto_now_add=True)

    subject = models.CharField(max_length=100)
    body = models.TextField()

    def unflag(self):
        self.flagged = False
        self.save()
        self.list.send_to_subscribers(self)

    def save(self, *args, **kwargs):
        already_sent = (self.pk is not None and not self.flagged)
        result = models.Model.save(self, *args, **kwargs)
        if self.pk is not None and not self.flagged and not already_sent:
            self.list.send_to_subscribers(self)
        return result

PERMISSIONS = (
    ("LIST_VIEW",
     ("see the list, and its archives if they're not private; "
      "and request subscription; and attempt to post messages")),
    ("LIST_SUBSCRIBE_SELF",
     "subscribe to the list without moderation"),
    ("LIST_POST",
     "post a message to the list without moderation"),
    ("LIST_POST_MODERATE", 
     "moderate queued posts"),
    ("LIST_ADD_SUBSCRIBERS",
     "initiate new subscription requests, to be moderated if necessary"),
    ("LIST_SUBSCRIBE_MODERATE", 
     "moderate subscription requests"),
    ("LIST_ADD_ALLOWED_SENDERS", 
     "grant other users the right to post to the list without moderation"),
    ("LIST_CONFIGURE",
     "edit the list's settings, including its security settings"),
    )

def apply_constraints(recommendations, constraints):
    permissions = []
    for permission in recommendations:
        if permission in constraints:
            permissions.append(permission)
    return permissions

class LocalRoles(models.Model):
    username = models.CharField(max_length=100, db_index=True)
    list = models.ForeignKey(MailingList)

    roles = models.TextField()

    def __unicode__(self):
        return "%s: %s" % (self.list, self.username)

    def get_roles(self):
        if not self.roles:
            return []
        return self.roles.split(',')

    def has_role(self, role):
        return role in self.get_roles()

    #def add_all_permissions(self):
    #    permissions = ','.join(PERMISSIONS.keys())
    #    self.permissions = permissions
    #    self.save()

    def add_role(self, role):
        roles = self.get_roles()
        if role not in roles:
            roles.append(role)
        self.roles = ','.join(roles)
        self.save()

    def remove_role(self, role):
        roles = self.get_roles()
        if role in roles:
            roles.remove(role)
        self.roles = roles
        self.save()

class RolePermissions(models.Model):
    list = models.ForeignKey(MailingList)
    role = models.CharField(max_length=100, db_index=True)
    
    permissions = models.TextField()

    def __unicode__(self):
        return "%s: %s" % (self.wiki, self.role)

    def get_permissions(self):
        if not self.permissions:
            return []
        return self.permissions.split(',')

    def set_permissions(self, permissions):
        if not permissions:
            self.permissions = ''
        self.permissions = ','.join(permissions)
        self.save()

    def has_permission(self, permission):
        return permission in self.get_permissions()

    #def add_all_permissions(self):
    #    permissions = ','.join(PERMISSIONS.keys())
    #    self.permissions = permissions
    #    self.save()

    def add_permission(self, permission):
        permissions = self.get_permissions()
        if permission not in permissions:
            permissions.append(permissions)
        self.permissions = permissions
        self.save()

    def remove_permission(self, permission):
        permissions = self.get_permissions()
        if permission in permissions:
            permissions.remove(permission)
        self.permissions = permissions
        self.save()
