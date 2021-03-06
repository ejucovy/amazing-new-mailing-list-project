from ConfigParser import RawConfigParser
from ConfigParser import (NoOptionError, NoSectionError, 
                          MissingSectionHeaderError)
from StringIO import StringIO

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models

from main.mail import EmailMessageWithEnvelopeTo

from listen.signals import *

class NoDefault(object):
    def __repr__(self):
        return "(no default)"
NoDefault = NoDefault()

class MailingList(models.Model):
    slug = models.CharField(max_length=100, unique=True)
    config = models.TextField(null=True, blank=True)

    container_id = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return self.slug

    @models.permalink
    def get_absolute_url(self):
        return ('mailing_list', [self.slug], {})

    def email_address(self):
        return "%s@%s" % (self.slug, self.fqdn)

    @property
    def fqdn(self):
        return settings.SITE_DOMAIN

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
        try:
            config.readfp(fp)
        except MissingSectionHeaderError:
            if default is NoDefault:
                raise
            return default
        try:
            value = config.get(section, key)
        except (NoOptionError,
                NoSectionError):
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

    @property
    def subscription_moderation_policy(self):
        policies = settings.LIST_SUBSCRIPTION_MODERATION_POLICIES
        policy_key = self.get_option("subscription_moderation_policy", asbool=False,
                                     default=policies[0][0])

        from listen.policies import get_subscription_policy
        policy = get_subscription_policy(policy_key)
        return policy

    @property
    def post_moderation_policy(self):
        policies = settings.LIST_POST_MODERATION_POLICIES
        policy_key = self.get_option("post_moderation_policy", asbool=False,
                                     default=policies[0][0])

        from listen.policies import get_post_policy
        policy = get_post_policy(policy_key)
        return policy
        
    def get_permissions(self, user):
        if user.is_superuser:
            return set(i[0] for i in PERMISSIONS)

        if user.is_authenticated() and user.is_active:
            username = user.username
            user_roles = LocalRoles.objects.filter(username=username, 
                                                   list=self)
            roles = set(["Authenticated"])
        else:
            user_roles = []
            roles = set(["Anonymous"])

        for user_role in user_roles:
            roles.update(user_role.get_roles())

        role_permissions = RolePermissions.objects.filter(
            list=self, role__in=roles)
        permissions = set()
        for role_permission in role_permissions:
            permissions.update(role_permission.get_permissions())
        return permissions
    
    def submit_subscription_request(self, user):
        return self.subscription_moderation_policy.process_request(self, user)

    def submit_post(self, author, subject, body):
        was_accepted, post, message_level, message = \
            self.post_moderation_policy.process_request(self, author, subject, body)
        post_submitted.send(sender=self.__class__, post=post, 
                            author=author, subject=subject, body=body)
        if was_accepted:
            post_accepted.send(sender=self.__class__, post=post, 
                               author=author, subject=subject, body=body)
        elif post is None:
            post_rejected.send(sender=self.__class__, post=post, 
                               author=author, subject=subject, body=body)

        return (was_accepted, post, message_level, message)

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

        if self.container_id:
            uid = "%s.%s" % (self.slug, self.container_id)
        else:
            uid = self.slug

        email = EmailMessageWithEnvelopeTo(
            subject, body, settings.DEFAULT_FROM_EMAIL, subscribers, 
            headers={
                'From': author,
                'To': self.email_address(),
                'List-ID': "<%s.%s>" % (uid, self.fqdn),
                'List-Help': "<mailto:%s+help@%s>" % (self.slug, self.fqdn),
                'List-Subscribe': "<mailto:%s+subscribe@%s" % (self.slug, self.fqdn),
                'List-Unsubscribe': "<mailto:%s+unsubscribe@%s" % (self.slug, self.fqdn),
                'List-Post': "<mailto:%s@%s" % (self.slug, self.fqdn), # XXX TODO "NO"
                'List-Owner': "<mailto:%s+manager@%s" % (self.slug, self.fqdn),
                'List-Archive': "<http://%s/%s>" % (self.fqdn, self.get_absolute_url()),
                })
        email.content_subtype = "text/html"
        email.send()

class MailingListPost(models.Model):
    author = models.ForeignKey("auth.user")
    list = models.ForeignKey(MailingList)

    flagged = models.BooleanField(default=False, db_index=True)

    created = models.DateTimeField(auto_now_add=True)

    subject = models.CharField(max_length=100)
    body = models.TextField()

    in_reply_to = models.ForeignKey('self', null=True)

    @models.permalink
    def get_absolute_url(self):
        return ('mailing_list_view_post', [self.list.slug, self.id], {})

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
        return "%s: %s" % (self.list, self.role)

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

class SubscriptionQueue(models.Model):
    list = models.ForeignKey(MailingList)
    user = models.ForeignKey("auth.user")

