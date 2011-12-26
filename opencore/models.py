from django.conf import settings
from django.db import models
from opencore import listeners
from main.email import EmailMessageWithEnvelopeTo

PROJECT_ROLES = (
    ("ProjectAdmin", "Project Admin"),
    ("ProjectMember", "Project Member"),
    )
PROJECT_POLICIES = (
    ("policy_medium", "Medium"),
    ("policy_closed", "Closed"),
    ("policy_open", "Open"),
    )

class Project(models.Model):
    slug = models.CharField(max_length=100, unique=True)
    policy = models.CharField(choices=PROJECT_POLICIES, max_length=100, db_index=True)

    @models.permalink
    def get_absolute_url(self):
        return ("project_home", [self.slug], {})

    def __unicode__(self):
        return u"%s: %s" % (self.slug, self.policy)

    @property
    def featurelets(self):
        return ["listen"]

    def members(self):
        return ProjectMember.objects.filter(project=self)

    def admins(self):
        return ProjectMember.objects.filter(project=self, role="ProjectAdmin")

    def has_member(self, user):
        if user.is_anonymous():
            return False
        try:
            return ProjectMember.objects.get(project=self, user=user)
        except ProjectMember.DoesNotExist:
            return False

    def viewable(self, request):
        if request.user.is_superuser:
            return True
        if self.policy in ("policy_medium", "policy_open"):
            return True
        if request.user.is_anonymous():
            return False
        try:
            membership = ProjectMember.objects.get(
                user=request.user, project=self)
        except ProjectMember.DoesNotExist:
            pass
        else:
            return True
        return False

    def manageable(self, request):
        if request.user.is_superuser:
            return True
        if request.user.is_anonymous():
            return False
        try:
            membership = ProjectMember.objects.get(user=request.user, project=self)
        except ProjectMember.DoesNotExist:
            return False
        if membership.role == "ProjectAdmin":
            return True
        return False

class ProjectMember(models.Model):
    user = models.ForeignKey("auth.User")
    project = models.ForeignKey(Project)
    role = models.CharField(choices=PROJECT_ROLES, max_length=100, db_index=True)

    def __unicode__(self):
        return u": ".join((unicode(self.user), unicode(self.project), self.role))

class ProjectInvite(models.Model):
    user = models.ForeignKey("auth.User")
    project = models.ForeignKey(Project)
    inviter = models.ForeignKey("auth.User", related_name="inviter")

    def remind(self, message=None):
        email = EmailMessageWithEnvelopeTo(
            "Reminder: Your invitation to join %s" % self.project,
            "Don't forget that you've been invited to join %s" % self.project + (
                '\n%s' % message if message else ''),
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email])
        email.send()

    def send(self, message=None):
        email = EmailMessageWithEnvelopeTo(
            "Invitation to join %s" % self.project,
            "You've been invited to join %s" % self.project + (
                '\n%s' % message if message else ''),
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email])
        email.send()

class ProjectRequest(models.Model):
    user = models.ForeignKey("auth.User")
    project = models.ForeignKey(Project)

    def send(self, message=None):
        email = EmailMessageWithEnvelopeTo(
            "Request to join %s" % self.project,
            "%s wants to join %s" % self.project + (
                '\n%s' % message if message else ''),
            settings.DEFAULT_FROM_EMAIL,
            [user.email for user in self.project.admins])
        email.send()
